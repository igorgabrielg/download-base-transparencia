import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Send, Bot, User, Loader2, Sparkles, MessageSquare, AlertCircle, FileText, ChevronDown, ChevronUp } from "lucide-react";
import toast from "react-hot-toast";

import { useChatIA } from "@/hooks/useConfig";

interface Message {
  id: string;
  sender: "user" | "bot";
  text: string;
  timestamp: Date;
  contexto?: string[];
}

export function ChatAuditoria() {
  const navigate = useNavigate();
  const chatIA = useChatIA();
  
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      sender: "bot",
      text: "Olá! Sou o **Auditor de IA Especialista em Orçamento**.\n\nFui treinado nas análises de Receitas e Despesas consolidadas a partir do Portal da Transparência.\n\nComo posso ajudar você nas auditorias e consultas fiscais hoje?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [expandedContextIndex, setExpandedContextIndex] = useState<Record<string, number | null>>({});
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Faz scroll automático até o final ao receber ou enviar mensagem
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, chatIA.isPending]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || chatIA.isPending) return;

    const userMessageText = input.trim();
    setInput("");

    const userMsg: Message = {
      id: `user-${Date.now()}`,
      sender: "user",
      text: userMessageText,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);

    chatIA.mutate(userMessageText, {
      onSuccess: (data) => {
        const botMsg: Message = {
          id: `bot-${Date.now()}`,
          sender: "bot",
          text: data.resposta,
          timestamp: new Date(),
          contexto: data.contexto,
        };
        setMessages((prev) => [...prev, botMsg]);
      },
      onError: (err: any) => {
        const errorMsg = err.response?.data?.detail || err.message || "Erro desconhecido";
        toast.error(`Falha ao obter resposta: ${errorMsg}`);
        
        const botMsg: Message = {
          id: `bot-err-${Date.now()}`,
          sender: "bot",
          text: `Desculpe, ocorreu um erro ao tentar processar sua pergunta: **${errorMsg}**.\n\nCertifique-se de que a indexação vetorial foi rodada na etapa 4.`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, botMsg]);
      },
    });
  };

  const toggleContext = (messageId: string, index: number) => {
    setExpandedContextIndex((prev) => {
      const current = prev[messageId];
      return {
        ...prev,
        [messageId]: current === index ? null : index,
      };
    });
  };

  // Helper simples para formatar negritos (**), parágrafos e listas
  const formatMessageText = (text: string) => {
    if (!text) return "";
    
    // Escapa caracteres simples de html para segurança
    let formatted = text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
      
    // Substitui **texto** por <strong>texto</strong>
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-[var(--theme-text)]">$1</strong>');
    
    const lines = formatted.split("\n");
    return lines.map((line, idx) => {
      const trimmed = line.trim();
      
      // Lista marcadas com - ou *
      if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
        const content = trimmed.substring(2);
        return (
          <li key={idx} className="ml-4 list-disc my-1 text-sm leading-relaxed" dangerouslySetInnerHTML={{ __html: content }} />
        );
      }
      
      // Subtítulo ###
      if (trimmed.startsWith("### ")) {
        const content = trimmed.substring(4);
        return (
          <h4 key={idx} className="text-sm font-semibold mt-3 mb-1 text-[var(--theme-text)]" dangerouslySetInnerHTML={{ __html: content }} />
        );
      }

      // Subtítulo ##
      if (trimmed.startsWith("## ")) {
        const content = trimmed.substring(3);
        return (
          <h3 key={idx} className="text-base font-bold mt-4 mb-2 text-[var(--theme-text)]" dangerouslySetInnerHTML={{ __html: content }} />
        );
      }
      
      // Parágrafo simples ou linha vazia
      if (trimmed === "") {
        return <div key={idx} className="h-2" />;
      }
      
      return (
        <p key={idx} className="text-sm leading-relaxed mb-2" dangerouslySetInnerHTML={{ __html: line }} />
      );
    });
  };

  // Verifica se a resposta do bot indica falha por falta de indexação vetorial
  const needsIndexing = (text: string) => {
    return text.includes("banco de dados vetorial") || text.includes("coleção de dados indexados") || text.includes("Indexação Vetorial");
  };

  return (
    <div className="flex flex-col h-[calc(100vh-100px)]">
      {/* Header Premium do Chat */}
      <div className="flex items-center justify-between p-4 rounded-t-lg bg-[var(--theme-surface-1)] border-b border-[var(--theme-border)] shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full flex items-center justify-center bg-[var(--theme-accent)]/10 text-[var(--theme-accent)] animate-pulse">
            <Bot size={22} />
          </div>
          <div>
            <h3 className="text-sm font-bold text-[var(--theme-text)] flex items-center gap-2">
              Auditor de Orçamento IA <span className="text-[10px] bg-[var(--theme-accent)]/10 text-[var(--theme-accent)] px-2 py-0.5 rounded-full font-normal">RAG Ativo</span>
            </h3>
            <p className="text-xs text-[var(--theme-text-secondary)]">Consulta em tempo real de receitas e despesas</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs text-[var(--theme-text-secondary)]">
          <Sparkles size={14} className="text-[var(--theme-warning)]" />
          <span>Focado nos relatórios consolidados</span>
        </div>
      </div>

      {/* Histórico de Mensagens */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-[var(--theme-bg-secondary)]/30 rounded-b-none border-x border-[var(--theme-border)]">
        {messages.map((msg) => {
          const isBot = msg.sender === "bot";
          const showIndexingBtn = isBot && needsIndexing(msg.text);
          
          return (
            <div key={msg.id} className={`flex gap-3 max-w-[85%] ${isBot ? "mr-auto" : "ml-auto flex-row-reverse"}`}>
              {/* Avatar */}
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white shrink-0 ${
                isBot ? "bg-[var(--theme-accent)]" : "bg-[var(--theme-surface-3)] text-[var(--theme-text)]"
              }`}>
                {isBot ? <Bot size={16} /> : <User size={16} className="text-[var(--theme-text)]" />}
              </div>

              {/* Balão de Chat */}
              <div className="space-y-2">
                <div className={`p-4 rounded-2xl shadow-sm border transition-all ${
                  isBot 
                    ? "bg-[var(--theme-surface-1)] border-[var(--theme-border)] rounded-tl-none text-[var(--theme-text)]" 
                    : "bg-[var(--theme-accent)]/10 border-[var(--theme-accent)]/30 rounded-tr-none text-[var(--theme-text)]"
                }`}>
                  <div className="space-y-1">
                    {formatMessageText(msg.text)}
                  </div>

                  {/* Botão de ação para redirecionar se faltar indexar */}
                  {showIndexingBtn && (
                    <button
                      onClick={() => navigate("/config/ia")}
                      className="mt-4 flex items-center gap-2 px-3 py-1.5 text-xs font-semibold rounded bg-[var(--theme-accent)] text-white hover:bg-[var(--theme-accent-hover)] transition-all cursor-pointer"
                    >
                      <Sparkles size={13} />
                      Ir para Configurações de IA & Indexar
                    </button>
                  )}
                  
                  <span className="block text-[9px] text-[var(--theme-text-secondary)] mt-2 text-right">
                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>

                {/* Referências de Contexto RAG */}
                {isBot && msg.contexto && msg.contexto.length > 0 && (
                  <div className="pl-2 space-y-1">
                    <span className="text-[10px] font-semibold text-[var(--theme-text-secondary)] flex items-center gap-1">
                      <FileText size={12} /> Fontes de dados utilizadas ({msg.contexto.length}):
                    </span>
                    <div className="grid grid-cols-1 gap-1">
                      {msg.contexto.map((chunk, index) => {
                        const isExpanded = expandedContextIndex[msg.id] === index;
                        return (
                          <div key={index} className="text-[11px] rounded border border-[var(--theme-border)] bg-[var(--theme-surface-1)]/60 overflow-hidden">
                            <button
                              onClick={() => toggleContext(msg.id, index)}
                              className="w-full flex items-center justify-between px-2 py-1 hover:bg-[var(--theme-surface-2)] transition-colors text-left font-mono text-[var(--theme-text-secondary)]"
                            >
                              <span className="truncate">Trecho do Relatório #{index + 1}</span>
                              {isExpanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                            </button>
                            {isExpanded && (
                              <div className="p-2 border-t border-[var(--theme-border)] bg-[var(--theme-surface-2)]/30 font-mono text-[10px] leading-relaxed text-[var(--theme-text)] whitespace-pre-wrap">
                                {chunk}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* Indicador de Carregamento */}
        {chatIA.isPending && (
          <div className="flex gap-3 max-w-[80%] mr-auto">
            <div className="w-8 h-8 rounded-full flex items-center justify-center bg-[var(--theme-accent)] text-white shrink-0">
              <Bot size={16} />
            </div>
            <div className="p-4 rounded-2xl bg-[var(--theme-surface-1)] border border-[var(--theme-border)] rounded-tl-none flex items-center gap-3">
              <Loader2 size={16} className="animate-spin text-[var(--theme-accent)]" />
              <span className="text-xs text-[var(--theme-text-secondary)] font-medium italic animate-pulse">
                O Auditor de IA está analisando os relatórios...
              </span>
            </div>
          </div>
        )}

        {/* Div invisível para scroll âncora */}
        <div ref={messagesEndRef} />
      </div>

      {/* Caixa de Entrada Inferior */}
      <form onSubmit={handleSend} className="p-3 bg-[var(--theme-surface-1)] border-x border-b border-[var(--theme-border)] rounded-b-lg shadow-sm flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={chatIA.isPending ? "Aguarde a resposta do auditor..." : "Pergunte sobre receitas, despesas, meta fiscal, ministérios..."}
          disabled={chatIA.isPending}
          className="flex-1 input-base rounded-full px-4 py-2.5 text-sm bg-[var(--theme-bg)] border-[var(--theme-border)] focus:border-[var(--theme-accent)] focus:ring-1 focus:ring-[var(--theme-accent)] transition-all disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={!input.trim() || chatIA.isPending}
          className="w-10 h-10 rounded-full bg-[var(--theme-accent)] text-white flex items-center justify-center hover:bg-[var(--theme-accent-hover)] transition-all shrink-0 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
          title="Enviar pergunta"
        >
          <Send size={16} />
        </button>
      </form>
    </div>
  );
}
