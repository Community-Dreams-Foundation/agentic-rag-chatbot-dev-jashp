"use client";

import React, { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";

// --- Types ---
type Message = {
  id: string;
  role: "user" | "agent" | "system";
  content: string;
  isStreaming?: boolean;
};

export default function TerminalUI() {
  // --- State ---
  const [history, setHistory] = useState<Message[]>([
    {
      id: "init",
      role: "system",
      content:
        "Welcome to Agentic RAG CLI. Type `/upload` to index a document, or ask a question.",
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  // --- Refs ---
  const bottomRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // --- Auto-Scroll Effect ---
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history]);

  // --- Handlers ---
  const handleCommand = async (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && inputValue.trim() && !isProcessing) {
      const command = inputValue.trim();
      setInputValue("");

      // 1. Handle special /upload command
      if (command.toLowerCase() === "/upload") {
        fileInputRef.current?.click();
        return;
      }

      // 2. Handle standard chat question
      const userMessage: Message = {
        id: Date.now().toString(),
        role: "user",
        content: command,
      };

      setHistory((prev) => [...prev, userMessage]);
      setIsProcessing(true);

      // TODO: Replace this timeout with your actual fetch/SSE call to the Python backend
      // Mocking a streaming response for UI testing
      setTimeout(() => {
        const agentMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "agent",
          content:
            "I found this in the architecture document. The system uses a LangGraph orchestration loop. [Source: ARCHITECTURE.md, Chunk: 04]",
        };
        setHistory((prev) => [...prev, agentMessage]);
        setIsProcessing(false);
      }, 1000);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const sysMsgUpload: Message = {
      id: Date.now().toString(),
      role: "system",
      content: `Uploading ${file.name} to the RAG pipeline...`,
    };
    setHistory((prev) => [...prev, sysMsgUpload]);

    // TODO: Implement FormData POST to Python FastAPI /ingest endpoint here 

    setTimeout(() => {
      setHistory((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "system",
          content: `Success: ${file.name} parsed, chunked, and indexed. Ready for queries.`,
        },
      ]);
      if (fileInputRef.current) fileInputRef.current.value = ""; // Reset input
    }, 1500);
  };

  // --- Constants ---
  const cliPrompt = "dev-jash15@agentic-rag:~$ ";

  // --- Render ---
  return (
    <div className="flex flex-col h-screen bg-slate-950 text-slate-300 font-mono text-sm sm:text-base overflow-hidden selection:bg-emerald-900 selection:text-emerald-100">
      {/* Hidden File Input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileUpload}
        className="hidden"
        accept=".pdf,.txt,.md,.html"
      />

      {/* Output History Area */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 pb-24 space-y-4 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
        {history.map((msg) => (
          <div key={msg.id} className="flex flex-col gap-1">
            {msg.role === "user" && (
              <div className="text-emerald-400">
                <span className="font-bold">{cliPrompt}</span>
                {msg.content}
              </div>
            )}

            {msg.role === "agent" && (
              <div className="text-slate-100 prose prose-invert prose-emerald max-w-none">
                <ReactMarkdown>{msg.content}</ReactMarkdown>
                {msg.isStreaming && <span className="animate-pulse">_</span>}
              </div>
            )}

            {msg.role === "system" && (
              <div className="text-amber-500/80 italic">
                {`> ${msg.content}`}
              </div>
            )}
          </div>
        ))}
        {/* Invisible div to scroll to */}
        <div ref={bottomRef} />
      </div>

      {/* Command Line Input Area */}
      <div className="fixed bottom-0 w-full bg-slate-950 p-4 sm:p-6 border-t border-slate-800">
        <div className="flex items-center gap-2 max-w-full">
          <span className="text-emerald-400 font-bold whitespace-nowrap">
            {cliPrompt}
          </span>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleCommand}
            disabled={isProcessing}
            className="flex-1 bg-transparent border-none outline-none text-slate-100 disabled:opacity-50 w-full"
            autoFocus
            spellCheck={false}
            autoComplete="off"
          />
        </div>
      </div>
    </div>
  );
}
