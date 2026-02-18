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

      // Handle special /upload command
      if (command.toLowerCase() === "/upload") {
        fileInputRef.current?.click();
        return;
      }

      // Handle standard chat question
      const userMessage: Message = {
        id: Date.now().toString(),
        role: "user",
        content: command,
      };

      setHistory((prev) => [...prev, userMessage]);
      setIsProcessing(true);

      // Create a temporary "streaming/loading" message
      const tempAgentMsgId = (Date.now() + 1).toString();
      setHistory((prev) => [
        ...prev,
        { id: tempAgentMsgId, role: "agent", content: "", isStreaming: true },
      ]);

      try {
        // Send the query to the FastAPI backend
        const response = await fetch("http://localhost:8000/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: command }),
        });

        if (!response.ok) throw new Error("Chat request failed");

        const data = await response.json();

        // Replace the temporary message with the actual agent response
        setHistory((prev) =>
          prev.map((msg) =>
            msg.id === tempAgentMsgId
              ? { ...msg, content: data.reply, isStreaming: false }
              : msg,
          ),
        );
      } catch (error) {
        setHistory((prev) =>
          prev.map((msg) =>
            msg.id === tempAgentMsgId
              ? {
                  ...msg,
                  content: "System Error: Could not reach the AI agent.",
                  isStreaming: false,
                }
              : msg,
          ),
        );
      } finally {
        setIsProcessing(false);
      }
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    // Grab all selected files into an array
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;

    const sysMsgUpload: Message = {
      id: Date.now().toString(),
      role: "system",
      content: `Uploading ${files.length} file(s) to the RAG pipeline...`,
    };
    setHistory((prev) => [...prev, sysMsgUpload]);

    // Append multiple files to the FormData object
    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file); // Note: "files" is plural now!
    });

    try {
      const response = await fetch("http://localhost:8000/api/ingest", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Ingestion failed");

      const data = await response.json();

      setHistory((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: "system",
          content: `Success: Processed ${files.length} file(s). ${data.total_chunks} total chunks indexed.`,
        },
      ]);
    } catch (error) {
      setHistory((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: "system",
          content: `System Error: Failed to index files. Ensure backend is running.`,
        },
      ]);
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
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
        multiple
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
