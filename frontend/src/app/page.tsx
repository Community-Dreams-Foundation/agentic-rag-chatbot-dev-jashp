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
        "Welcome to Agentic RAG CLI. Type `/upload` to index a document(s), or ask a question.",
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
  const handleCommand = async (
    e: React.KeyboardEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
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
  const cliPrompt = "dev-jash@agentic-rag:~$ ";

  const getStatusMessage = (input: string) => {
    const cmd = input.toLowerCase();

    // Feature C: Python & Weather Logic
    if (cmd.includes("weather") || cmd.includes("temperature")) {
      return "Accessing Open-Meteo API...";
    }
    if (
      cmd.includes("python") ||
      cmd.includes("script") ||
      cmd.includes("calculate") ||
      cmd.includes("compare")
    ) {
      return "Executing Python sandbox...";
    }

    // Feature A: RAG Logic
    if (
      cmd.includes("document") ||
      cmd.includes("project") ||
      cmd.includes("what is") ||
      cmd.includes("about")
    ) {
      return "Searching indexed documents...";
    }

    // Default Fallback
    return "Agentic RAG is thinking...";
  };

  // --- Render ---
  return (
    // Added w-full to ensure the main screen is strictly locked to the viewport width
    <div className="flex flex-col h-screen w-full bg-slate-950 text-slate-300 font-mono text-sm sm:text-base overflow-hidden selection:bg-emerald-900 selection:text-emerald-100">
      {/* Hidden File Input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileUpload}
        className="hidden"
        accept=".pdf,.txt,.md,.html"
        multiple
      />
      <div className="flex-1 overflow-y-auto overflow-x-hidden p-4 sm:p-6 space-y-4 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent w-full">
        {history.map((msg) => (
          <div key={msg.id} className="flex flex-col gap-1 w-full max-w-full">
            {msg.role === "user" && (
              <div className="text-emerald-400 break-words whitespace-pre-wrap">
                {/* FIX 2: Added whitespace-pre-wrap to force the string to respect the container width */}
                <span className="font-bold">{cliPrompt}</span>
                {msg.content}
              </div>
            )}

            {msg.role === "agent" && (
              <div className="text-slate-100 prose prose-invert prose-emerald max-w-none break-words">
                {msg.isStreaming && !msg.content ? (
                  <div className="flex items-center gap-2 text-emerald-500/60 font-mono italic">
                    <span className="animate-spin h-3 w-3 border-2 border-emerald-500 border-t-transparent rounded-full" />
                    <span>
                      {getStatusMessage(
                        history[history.length - 2]?.content || "",
                      )}
                    </span>
                  </div>
                ) : (
                  <div className="flex flex-col gap-2">
                    <ReactMarkdown
                      components={{
                        p: ({ children }) => {
                          if (typeof children === "string") {
                            // Regex to find [Source: X, Chunk: Y]
                            const parts = children.split(
                              /(\[Source:.*?, Chunk:.*?\])/g,
                            );
                            return (
                              <p>
                                {parts.map((part, i) =>
                                  part.startsWith("[Source:") ? (
                                    <span
                                      key={i}
                                      className="text-slate-400 text-[10px] font-mono bg-slate-800/40 px-1.5 py-0.5 rounded border border-slate-700/50 ml-1 inline-block align-middle"
                                    >
                                      {part}
                                    </span>
                                  ) : (
                                    part
                                  ),
                                )}
                              </p>
                            );
                          }
                          return <p>{children}</p>;
                        },
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                    {msg.isStreaming && (
                      <span className="animate-pulse text-emerald-400">_</span>
                    )}
                  </div>
                )}
              </div>
            )}

            {msg.role === "system" && (
              <div className="text-amber-500/80 italic break-words whitespace-pre-wrap">
                {`> ${msg.content}`}
              </div>
            )}
          </div>
        ))}
        {/* Invisible div to scroll to */}
        <div ref={bottomRef} className="h-2" />
      </div>

      {/* Command Line Input Area */}
      <div className="shrink-0 bg-slate-950 p-4 sm:p-6 border-t border-slate-800 w-full">
        {/* FIX 2: Changed 'items-center' to 'items-start' so the green prompt stays pinned to the top line as the box grows */}
        <div className="flex items-start gap-2 max-w-full">
          {/* FIX 3: Added a tiny padding-top (pt-[2px]) to perfectly align the span baseline with the textarea text */}
          <span className="text-emerald-400 font-bold whitespace-nowrap pt-[2px]">
            {cliPrompt}
          </span>

          {/* FIX 4: Swapped <input> for a magical auto-expanding <textarea> */}
          <textarea
            value={inputValue}
            onChange={(e) => {
              setInputValue(e.target.value);
              // Instantly auto-expand the height as the user types multiple lines
              e.target.style.height = "auto";
              e.target.style.height = `${e.target.scrollHeight}px`;
            }}
            onKeyDown={(e) => {
              // Pressing 'Enter' submits the prompt. 'Shift+Enter' will allow a manual new line.
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault(); // Stop it from creating a blank new line
                handleCommand(e);
                // Reset the box height back to 1 row after submitting
                (e.target as HTMLTextAreaElement).style.height = "auto";
              }
            }}
            disabled={isProcessing}
            className="flex-1 bg-transparent border-none outline-none text-slate-100 disabled:opacity-50 w-full min-w-0 resize-none overflow-hidden max-h-40 leading-normal"
            rows={1}
            autoFocus
            spellCheck={false}
            autoComplete="off"
          />
        </div>
      </div>
    </div>
  );
}
