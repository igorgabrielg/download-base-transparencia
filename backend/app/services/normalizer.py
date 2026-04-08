import re
import glob
from pathlib import Path
import pandas as pd

class Normalizer:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)

    def clean_monetary_value(self, val) -> float:
        """Limpa valores monetários representados como strings e os converte para float."""
        if pd.isna(val) or val is None:
            return 0.0
        
        if isinstance(val, (int, float)):
            return float(val)
        
        val_str = str(val).strip()
        
        # Remove símbolos de moeda como R$, $, etc.
        val_str = re.sub(r"[R\$\s\xa0]", "", val_str)
        
        # Caso o valor tenha o padrão brasileiro (pontos para milhares e vírgula para decimal):
        # Ex: "1.500.000,00" ou "500,00"
        if "," in val_str:
            # Se tiver pontos e vírgula, removemos os pontos e trocamos a vírgula por ponto
            if "." in val_str:
                val_str = val_str.replace(".", "")
            val_str = val_str.replace(",", ".")
        
        try:
            return float(val_str)
        except ValueError:
            return 0.0

    def extract_ano(self, df: pd.DataFrame, filepath: str = None) -> pd.Series:
        """Extrai o ano de 4 dígitos a partir de colunas temporais comuns como 'anoMes', 'ano', 'exercicio'
        ou do próprio nome do arquivo caso não existam no DataFrame.
        """
        # Procuramos colunas candidatas para o tempo
        cols = [c.lower() for c in df.columns]
        
        time_col = None
        for candidate in ["anomes", "ano_mes", "ano", "exercicio", "exercício"]:
            if candidate in cols:
                time_col = df.columns[cols.index(candidate)]
                break
        
        if time_col is not None:
            def parse_val(v):
                v_str = str(v).strip()
                # Se for anoMes no formato YYYYMM (ex: "202401" ou 202401) ou YYYY-MM
                clean_str = re.sub(r"\D", "", v_str) # remove não dígitos
                if len(clean_str) >= 4:
                    return clean_str[:4]
                return "0000"
            return df[time_col].apply(parse_val)
            
        # Caso não ache coluna temporal, tenta extrair o ano a partir do nome do arquivo (ex: receitas_2024.csv)
        if filepath:
            filename = Path(filepath).name
            match = re.search(r"\b(20[0-9]{2})\b", filename)
            if match:
                ano_detectado = match.group(1)
                return pd.Series([ano_detectado] * len(df))
                
        raise ValueError(f"Nenhuma coluna de ano/anoMes/exercicio encontrada no DataFrame. Colunas: {df.columns.tolist()}")

    def to_snake_case(self, name: str) -> str:
        """Converte uma string camelCase ou com espaços para snake_case."""
        name = str(name).strip()
        # Substitui acentuações e caracteres especiais
        # (Um mapeamento simples para letras básicas)
        import unicodedata
        name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
        
        # Insere underscores antes de letras maiúsculas
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
        
        # Substitui caracteres não alfanuméricos por underscores e reduz múltiplos underscores
        s3 = re.sub(r'[^a-zA-Z0-9]', '_', s2).lower()
        s4 = re.sub(r'_+', '_', s3)
        return s4.strip('_')

    def normalize_csv_files(self, prefix: str) -> pd.DataFrame:
        """Lê todos os arquivos CSV com o prefixo dado, normaliza as colunas e junta em um único DataFrame."""
        # Busca padrão com ano e mês (ex: despesas_2024_01.csv)
        pattern_month = str(self.data_dir / f"{prefix}_[0-9][0-9][0-9][0-9]_[0-9][0-9].csv")
        # Busca padrão apenas com ano (ex: receitas_2024.csv)
        pattern_year = str(self.data_dir / f"{prefix}_[0-9][0-9][0-9][0-9].csv")
        
        files = glob.glob(pattern_month) + glob.glob(pattern_year)
        
        if not files:
            print(f"Nenhum arquivo encontrado para os padrões: {pattern_month} ou {pattern_year}")
            return pd.DataFrame()
            
        dfs = []
        for file in files:
            print(f"Normalizando arquivo bruto: {file}")
            df = pd.read_csv(file)
            if df.empty:
                continue
                
            # 1. Padronização temporal para 'ano'
            df['ano'] = self.extract_ano(df, filepath=file)
            
            # Removemos colunas temporais antigas para unificar apenas na coluna 'ano'
            cols_to_drop = [c for c in df.columns if c.lower() in ["anomes", "ano_mes", "ano_fim", "ano_inicio", "mes_ano"]]
            df = df.drop(columns=cols_to_drop, errors="ignore")
            
            # 2. Padronização de nomes de colunas para snake_case
            df.columns = [self.to_snake_case(c) for c in df.columns]
            
            dfs.append(df)
            
        if not dfs:
            return pd.DataFrame()
            
        consolidated_df = pd.concat(dfs, ignore_index=True)
        
        # 3. Tipagem estrita de colunas monetárias
        # Identifica colunas monetárias prováveis no DataFrame resultante
        monetary_cols = [
            "valor", 
            "receita_realizada", 
            "orcamento_atualizado", 
            "receita_prevista", 
            "valor_recebido"
        ]
        for col in monetary_cols:
            if col in consolidated_df.columns:
                consolidated_df[col] = consolidated_df[col].apply(self.clean_monetary_value)
                
        # Garante que 'ano' é string de 4 dígitos
        if 'ano' in consolidated_df.columns:
            consolidated_df['ano'] = consolidated_df['ano'].astype(str)
            
        return consolidated_df

    def process(self):
        """Executa a normalização para Despesas e Receitas e salva no disco."""
        # Processa Despesas
        print("Iniciando normalização de Despesas...")
        df_despesas = self.normalize_csv_files("despesas")
        if not df_despesas.empty:
            out_path = self.data_dir / "despesas_normalizado.csv"
            df_despesas.to_csv(out_path, index=False)
            print(f"Salvo despesas normalizadas em: {out_path} ({len(df_despesas)} registros)")
        else:
            print("Nenhum dado de Despesas normalizado.")

        # Processa Receitas
        print("Iniciando normalização de Receitas...")
        df_receitas = self.normalize_csv_files("receitas")
        if not df_receitas.empty:
            out_path = self.data_dir / "receitas_normalizado.csv"
            df_receitas.to_csv(out_path, index=False)
            print(f"Salvo receitas normalizadas em: {out_path} ({len(df_receitas)} registros)")
        else:
            print("Nenhum dado de Receitas normalizado.")

if __name__ == "__main__":
    normalizer = Normalizer()
    normalizer.process()
