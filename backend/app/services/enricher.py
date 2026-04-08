import json
from pathlib import Path
import pandas as pd

class Enricher:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        
        # Mapeamento estático de descrições institucionais de ministérios comuns (Governo Federal)
        self.descricoes_ministerios = {
            "26000": "Órgão do Poder Executivo Federal responsável pela formulação e execução da política nacional de educação, abrangendo o ensino infantil, fundamental, médio, superior, profissionalizante e tecnológico.",
            "30000": "Órgão responsável pela defesa da ordem jurídica, dos direitos políticos e das garantias constitucionais, além da formulação e execução da política nacional de segurança pública e defesa social.",
            "52000": "Órgão responsável pela política de defesa nacional, pelo preparo e emprego das Forças Armadas (Marinha, Exército e Aeronáutica) e pela garantia da soberania e integridade do território brasileiro.",
            "41000": "Órgão encarregado de formular a política nacional de telecomunicações, radiodifusão e serviços postais, buscando a inclusão digital e universalização das comunicações.",
        }

        # Mapeamento estático de descrições de UGs comuns
        self.descricoes_ugs = {
            "200331": "Unidade responsável pelo gerenciamento descentralizado e aplicação de recursos orçamentários voltados às ações locais de segurança pública e policiamento preventivo/repressivo da Polícia Federal.",
            "153061": "Unidade gestora responsável pela execução financeira, acadêmica e administrativa da Universidade Federal de Juiz de Fora (UFJF).",
            "120195": "Centro militar focado na execução de compras, contratações e logística de suprimentos de aviação e infraestrutura do Comando da Aeronáutica.",
            "155013": "Hospital universitário integrado à rede Ebserh, focado em prestação de assistência médico-hospitalar pública gratuita e apoio ao ensino de saúde.",
            "153173": "Fundo Nacional de Desenvolvimento da Educação, responsável pela execução e repasses de programas nacionais voltados ao fomento da educação básica pública.",
            "154080": "Unidade gestora responsável pela infraestrutura e execução orçamentária do campus e atividades acadêmicas da Universidade Federal de Roraima (UFRR).",
            "153079": "Unidade gestora central da Universidade Federal do Paraná (UFPR), responsável pelas contas, despesas de custeio e investimentos da instituição."
        }

    def get_ministerio_descricao(self, cod_superior: str, nome: str) -> str:
        cod_str = str(cod_superior).strip()
        return self.descricoes_ministerios.get(
            cod_str, 
            f"Órgão superior da administração pública federal ({nome}) responsável pela coordenação, execução e planejamento de políticas públicas em seu setor de competência."
        )

    def get_ug_descricao(self, cod_ug: str, nome: str) -> str:
        cod_str = str(cod_ug).strip()
        return self.descricoes_ugs.get(
            cod_str, 
            f"Unidade Gestora (UG - {nome}) responsável por executar os recursos públicos orçamentários autorizados no âmbito de sua atuação regional ou setorial."
        )

    def build_dictionaries(self, df_despesas: pd.DataFrame, df_receitas: pd.DataFrame):
        """Gera e salva os dicionários independentes de Ministérios e UGs baseados nas bases,
        preservando dados existentes nos arquivos JSON originais.
        """
        min_path = self.data_dir / "dicionario_ministerios.json"
        ug_path = self.data_dir / "dicionario_ugs.json"
        
        # 1. Carrega os dicionários existentes
        ministerios = {}
        if min_path.exists():
            try:
                with open(min_path, "r", encoding="utf-8") as f:
                    ministerios = json.load(f)
            except Exception as e:
                print(f"Erro ao carregar dicionario_ministerios.json: {e}")
                
        ugs = {}
        if ug_path.exists():
            try:
                with open(ug_path, "r", encoding="utf-8") as f:
                    ugs = json.load(f)
            except Exception as e:
                print(f"Erro ao carregar dicionario_ugs.json: {e}")

        # 2. Processa Ministérios a partir de despesas e receitas
        # Mapeamos codigo_orgao_superior -> nome e descricao
        for df in [df_despesas, df_receitas]:
            if df.empty:
                continue
            
            # Identificando as colunas no df
            cod_col = "codigo_orgao_superior"
            nome_col = "nome_orgao_superior"
            
            if cod_col in df.columns and nome_col in df.columns:
                for _, row in df[[cod_col, nome_col]].drop_duplicates().iterrows():
                    cod = str(row[cod_col]).strip()
                    nome = str(row[nome_col]).strip()
                    if cod and cod != "nan":
                        # Só adiciona se não existir para preservar as descrições originais
                        if cod not in ministerios:
                            ministerios[cod] = {
                                "nome": nome,
                                "descricao": self.get_ministerio_descricao(cod, nome)
                            }
                        elif nome and nome != "nan":
                            # Se o nome estiver em branco no dicionário existente, atualiza
                            if not ministerios[cod].get("nome"):
                                ministerios[cod]["nome"] = nome

        # 3. Processa UGs a partir de despesas
        if not df_despesas.empty:
            cod_col = "codigo_ug"
            nome_col = "nome_ug"
            if cod_col in df_despesas.columns and nome_col in df_despesas.columns:
                for _, row in df_despesas[[cod_col, nome_col]].drop_duplicates().iterrows():
                    cod = str(row[cod_col]).strip()
                    nome = str(row[nome_col]).strip()
                    if cod and cod != "nan":
                        if cod not in ugs:
                            ugs[cod] = {
                                "nome": nome,
                                "descricao": self.get_ug_descricao(cod, nome)
                            }
                        elif nome and nome != "nan":
                            if not ugs[cod].get("nome"):
                                ugs[cod]["nome"] = nome

        # Salva dicionários atualizados
        with open(min_path, "w", encoding="utf-8") as f:
            json.dump(ministerios, f, indent=2, ensure_ascii=False)
        print(f"Salvo dicionário_ministerios.json ({len(ministerios)} registros)")

        with open(ug_path, "w", encoding="utf-8") as f:
            json.dump(ugs, f, indent=2, ensure_ascii=False)
        print(f"Salvo dicionário_ugs.json ({len(ugs)} registros)")

        return ministerios, ugs

    def enrich_despesas(self, df_despesas: pd.DataFrame, dict_min: dict, dict_ugs: dict) -> dict:
        """Processa cálculos matemáticos, cruzamento contextual e gera o JSON de Despesa."""
        if df_despesas.empty:
            return {}

        # 1. Total Geral de Despesas
        total_despesas = float(df_despesas["valor"].sum())

        # 2. Agrupamento por Órgão Superior (Ministério)
        despesas_por_orgao = df_despesas.groupby(["codigo_orgao_superior", "nome_orgao_superior"])["valor"].sum().reset_index()
        orgaos_resumo = []
        for _, row in despesas_por_orgao.iterrows():
            cod = str(row["codigo_orgao_superior"])
            orgaos_resumo.append({
                "codigo": cod,
                "nome": row["nome_orgao_superior"],
                "total_gasto": float(row["valor"]),
                "descricao": dict_min.get(cod, {}).get("descricao", "")
            })

        # 3. Agrupamento por UG para identificar a UG líder de gastos
        despesas_por_ug = df_despesas.groupby(["codigo_ug", "nome_ug", "codigo_orgao_superior"])["valor"].sum().reset_index()
        
        # Identifica automaticamente a UG líder
        ug_lider_row = despesas_por_ug.loc[despesas_por_ug["valor"].idxmax()]
        cod_ug_lider = str(ug_lider_row["codigo_ug"])
        nome_ug_lider = str(ug_lider_row["nome_ug"])
        valor_ug_lider = float(ug_lider_row["valor"])
        cod_min_lider = str(ug_lider_row["codigo_orgao_superior"])

        # Cruzamento Contextual para a UG Líder e seu Ministério
        ug_lider_contexto = {
            "codigo_ug": cod_ug_lider,
            "nome_ug": nome_ug_lider,
            "total_gasto": valor_ug_lider,
            "descricao_ug": dict_ugs.get(cod_ug_lider, {}).get("descricao", ""),
            "codigo_ministerio": cod_min_lider,
            "nome_ministerio": dict_min.get(cod_min_lider, {}).get("nome", ""),
            "descricao_ministerio": dict_min.get(cod_min_lider, {}).get("descricao", "")
        }

        # Lista de todas as UGs com seus totais
        ugs_resumo = []
        for _, row in despesas_por_ug.iterrows():
            cod_ug = str(row["codigo_ug"])
            ugs_resumo.append({
                "codigo_ug": cod_ug,
                "nome_ug": row["nome_ug"],
                "total_gasto": float(row["valor"]),
                "codigo_ministerio": str(row["codigo_orgao_superior"]),
                "descricao": dict_ugs.get(cod_ug, {}).get("descricao", "")
            })

        # Registros individuais estruturados
        registros = df_despesas.to_dict(orient="records")

        # JSON final consolidado e enriquecido de despesas
        json_despesas = {
            "tipo_dado": "despesas",
            "total_geral": total_despesas,
            "ug_lider_gastos": ug_lider_contexto,
            "resumo_orgaos": orgaos_resumo,
            "resumo_ugs": ugs_resumo,
            "dados_brutos": registros
        }

        # Salva o arquivo JSON
        with open(self.data_dir / "despesas_enriquecida.json", "w", encoding="utf-8") as f:
            json.dump(json_despesas, f, indent=2, ensure_ascii=False)
        print("Salvo despesas_enriquecida.json")

        return json_despesas

    def enrich_receitas(self, df_receitas: pd.DataFrame, dict_min: dict) -> dict:
        """Processa cálculos matemáticos, calcula desvios e gera o JSON de Receita."""
        if df_receitas.empty:
            return {}

        # 1. Cálculos de Desvio: receita_realizada - orcamento_atualizado
        df_receitas["desvio"] = df_receitas["receita_realizada"] - df_receitas["orcamento_atualizado"]
        
        # Média ponderada do % Previsto/Realizado: (total realizada / total orçado) * 100
        total_orcado = df_receitas["orcamento_atualizado"].sum()
        total_realizado = df_receitas["receita_realizada"].sum()
        
        if total_orcado > 0:
            media_ponderada_realizado = float((total_realizado / total_orcado) * 100)
        else:
            media_ponderada_realizado = 0.0

        # Percentual de realização de cada linha
        realizacao_percent = []
        for _, row in df_receitas.iterrows():
            orc = row["orcamento_atualizado"]
            real = row["receita_realizada"]
            percent = float((real / orc) * 100) if orc > 0 else 0.0
            realizacao_percent.append(percent)
        df_receitas["percentual_realizado"] = realizacao_percent

        # 2. Resumo por Órgão Superior (Ministério)
        receitas_por_orgao = df_receitas.groupby(["codigo_orgao_superior", "nome_orgao_superior"]).agg(
            total_orcado=("orcamento_atualizado", "sum"),
            total_realizado=("receita_realizada", "sum")
        ).reset_index()

        orgaos_resumo = []
        for _, row in receitas_por_orgao.iterrows():
            cod = str(row["codigo_orgao_superior"])
            orc = float(row["total_orcado"])
            real = float(row["total_realizado"])
            desvio = real - orc
            percent = (real / orc) * 100 if orc > 0 else 0.0
            
            orgaos_resumo.append({
                "codigo": cod,
                "nome": row["nome_orgao_superior"],
                "total_orcado": orc,
                "total_realizado": real,
                "desvio_nominal": desvio,
                "percentual_realizado": float(percent),
                "descricao": dict_min.get(cod, {}).get("descricao", "")
            })

        # Registros individuais
        registros = df_receitas.to_dict(orient="records")

        # JSON final consolidado de receitas
        json_receitas = {
            "tipo_dado": "receitas",
            "total_orcado": float(total_orcado),
            "total_realizado": float(total_realizado),
            "desvio_global": float(total_realizado - total_orcado),
            "percentual_realizado_medio_ponderado": media_ponderada_realizado,
            "resumo_orgaos": orgaos_resumo,
            "dados_brutos": registros
        }

        # Salva o arquivo JSON
        with open(self.data_dir / "receitas_enriquecida.json", "w", encoding="utf-8") as f:
            json.dump(json_receitas, f, indent=2, ensure_ascii=False)
        print("Salvo receitas_enriquecida.json")

        return json_receitas

    def process(self):
        """Lê os CSVs normalizados, gera os dicionários e arquivos finais JSON enriquecidos."""
        despesas_path = self.data_dir / "despesas_normalizado.csv"
        receitas_path = self.data_dir / "receitas_normalizado.csv"

        df_despesas = pd.read_csv(despesas_path) if despesas_path.exists() else pd.DataFrame()
        df_receitas = pd.read_csv(receitas_path) if receitas_path.exists() else pd.DataFrame()

        if df_despesas.empty and df_receitas.empty:
            print("Nenhum arquivo normalizado encontrado para enriquecer.")
            return

        # 1. Constrói dicionários independentes
        dict_min, dict_ugs = self.build_dictionaries(df_despesas, df_receitas)

        # 2. Enriquece Despesas
        self.enrich_despesas(df_despesas, dict_min, dict_ugs)

        # 3. Enriquece Receitas
        self.enrich_receitas(df_receitas, dict_min)

if __name__ == "__main__":
    enricher = Enricher()
    enricher.process()
