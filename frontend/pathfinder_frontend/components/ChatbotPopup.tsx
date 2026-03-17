"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Image from "next/image";
import { Card, CardHeader, CardBody, CardFooter, Button, Chip, Textarea, Avatar, Badge, Spacer, Divider } from "@heroui/react";

interface Message {
  role: "user" | "model";
  parts: { text: string }[];
}

const STARTER_QUESTIONS = [
  "How can I improve my cv? ",
  "Technical Interview tips?",
  "What does a Data Scientist do?",
  "Business Analyst skills?"
];

//  Sub-component: Typewriter Effect from hero  ui
const Typewriter = ({ text, onComplete, skip }: { text: string, onComplete?: () => void, skip?: boolean }) => {
  const [displayedText, setDisplayedText] = useState("");
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (skip) {
      setDisplayedText(text);
      if (onComplete && index < text.length) onComplete();
      setIndex(text.length);
      return;
    }

    if (index < text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText((prev) => prev + text[index]);
        setIndex((prev) => prev + 1);
      }, 10); // Standardize speed
      return () => clearTimeout(timeout);
    } else if (onComplete && index === text.length && displayedText.length > 0 && !skip) {
      // Trigger onComplete only once when naturally reaching the end
      onComplete();
    }
  }, [index, text, onComplete, skip, displayedText.length]);

  return <span>{displayedText}</span>;
};

export default function ChatbotPopup() {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [history, setHistory] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [skipTyping, setSkipTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const API_URL = "http://localhost:8002/api/chat";

  // Material Auto-scroll
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: "smooth"
      });
    }
  }, [history, isLoading, isTyping]);

  const handleSend = async (customMsg?: string) => {
    const textToSend = customMsg || message.trim();
    if (!textToSend || isLoading || isTyping) return;

    setMessage("");
    setIsLoading(true);
    setIsTyping(false);
    setSkipTyping(false);

    const newUserMsg: Message = { role: "user", parts: [{ text: textToSend }] };
    setHistory((prev) => [...prev, newUserMsg]);

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        signal: controller.signal,
        body: JSON.stringify({
          user_id: "test_user",
          message: textToSend,
          history: history,
        }),
      });

      if (!response.ok) throw new Error("API Error");

      const data = await response.json();
      setIsTyping(true); // Start typing animation
      setHistory((prev) => [
        ...prev,
        { role: "model", parts: [{ text: data.reply }] },
      ]);
    } catch (error: any) {
      if (error.name === "AbortError") {
        console.log("Fetch aborted by user");
        return; // Don't show error message or change state if user manually aborted
      }
      console.error("Chat Error:", error);
      setHistory((prev) => [
        ...prev,
        { role: "model", parts: [{ text: "I'm having a technical issue. Please try again later." }] },
      ]);
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end font-sans">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 30, scale: 0.95, filter: "blur(4px)" }}
            animate={{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)" }}
            exit={{ opacity: 0, y: 30, scale: 0.95, filter: "blur(4px)" }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="mb-6 z-50"
          >
            <Card
              className="h-[500px] w-[360px] max-w-[90vw] bg-white/90 backdrop-blur-3xl shadow-[0_32px_128px_-32px_rgba(0,0,0,0.3)] border-2 border-purple-800 rounded-[2rem] overflow-hidden"
              shadow="lg"
            >
              {/* Header  */}
              <CardHeader className="flex justify-between items-center px-6 py-5 bg-white/50 border-b border-divider/50">
                <div className="flex items-center gap-3.5">
                  <Badge
                    content=""
                    color="success"
                    shape="circle"
                    placement="bottom-right"
                    className="border-2 border-white ring-1 ring-black/5"
                  >
                    <Avatar
                      src="/model.png"
                      className="w-11 h-11 border-2 border-purple-100 shadow-sm"
                      isBordered
                      color="secondary"
                    />
                  </Badge>
                  <div>
                    <h3 className="text-[15px] font-black tracking-tight text-foreground leading-none">PathFinder+ AI</h3>
                    <Spacer y={1} />
                    <p className="text-[10px] font-bold text-success uppercase tracking-[0.1em] opacity-80">Expert Advisor</p>
                  </div>
                </div>
                <div className="flex gap-1.5">
                  {history.length > 0 && (
                    <Button
                      size="sm"
                      variant="light"
                      color="secondary"
                      className="text-[10px] font-black uppercase tracking-widest min-w-unit-12 h-8"
                      onClick={() => setHistory([])}
                    >
                      Reset
                    </Button>
                  )}
                  <Button
                    isIconOnly
                    size="sm"
                    radius="full"
                    variant="flat"
                    onClick={() => setIsOpen(false)}
                    className="bg-default-100/50 hover:bg-default-200/80 transition-colors w-8 h-8"
                  >
                    <span className="text-sm font-bold opacity-70">✕</span>
                  </Button>
                </div>
              </CardHeader>

              {/* Easy scroll */}
              <CardBody
                ref={scrollRef}
                className="flex-1 overflow-y-auto px-6 py-10 space-y-8 scrollbar-hide bg-gradient-to-b from-transparent via-white/10 to-white/40"
              >
                <AnimatePresence mode="popLayout">
                  {history.length === 0 && (
                    <motion.div
                      initial={{ opacity: 0, y: 15 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex flex-col items-center justify-center h-full text-center space-y-8 py-10"
                    >
                      <div className="relative">
                        <Avatar
                          src="/model.png"
                          className="w-28 h-28 shadow-[0_20px_60px_-15px_rgba(147,51,234,0.3)] ring-offset-4 ring-4 ring-purple-100"
                        />
                        <motion.div
                          animate={{ scale: [1, 1.2, 1] }}
                          transition={{ repeat: Infinity, duration: 2 }}
                          className="absolute -top-1 -right-1 w-6 h-6 bg-purple-600 rounded-full border-4 border-white shadow-lg"
                        />
                      </div>
                      <div className="space-y-4">
                        <h2 className="text-3xl font-black tracking-tighter text-foreground">Insight awaits.</h2>
                        <p className="text-sm font-medium text-default-500 max-w-[300px] leading-relaxed">
                          Your senior academic & career consultant, specialized for Sri Lanka.
                        </p>
                      </div>
                    </motion.div>
                  )}

                  {history.map((msg, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, y: 15, scale: 0.98 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      className={`flex items-start gap-4 ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}
                    >
                      <Avatar
                        src={msg.role === "user" ? "/user.png" : "/model.png"}
                        size="sm"
                        className={`flex-shrink-0 shadow-md border-2 border-white ring-1 ring-black/5 ${msg.role === "user" ? "bg-purple-50" : "bg-white"}`}
                      />

                      <Card
                        shadow="none"
                        className={`max-w-[85%] px-5 py-4 border-none shadow-sm ${msg.role === "user"
                          ? "bg-purple-600 text-white rounded-tr-none font-semibold leading-relaxed"
                          : "bg-default-50/80 text-foreground rounded-tl-none ring-1 ring-default-200/50 leading-relaxed font-medium"
                          }`}
                      >
                        <p className="text-[13px]">
                          {msg.role === "model" && i === history.length - 1 ? (
                            <Typewriter
                              text={msg.parts[0].text}
                              skip={skipTyping}
                              onComplete={() => setIsTyping(false)}
                            />
                          ) : (
                            msg.parts[0].text
                          )}
                        </p>
                      </Card>
                    </motion.div>
                  ))}

                  {isLoading && (
                    <div className="flex items-center gap-3 pl-12 text-[10px] font-black text-purple-600/60 uppercase tracking-[0.2em] italic animate-pulse">
                      Synthesizing intelligence for user...
                    </div>
                  )}
                </AnimatePresence>
              </CardBody>

              {/*  Professional Input Section */}
              <CardFooter className="flex flex-col p-5 pt-4 bg-white border-t border-divider/50 shadow-[0_-10px_40px_-5px_rgba(0,0,0,0.03)] pb-4">
                {/* Starter Chips: Material Style */}
                {history.length < 3 && (
                  <div className="flex flex-wrap gap-2 mb-4 w-full">
                    {STARTER_QUESTIONS.map((q, idx) => (
                      <Chip
                        key={idx}
                        as="button"
                        variant="flat"
                        color="secondary"
                        onClick={() => handleSend(q)}
                        className="font-bold text-[9px] border-none bg-purple-50 hover:bg-purple-100 transition-all cursor-pointer px-1 active:scale-95 h-6 uppercase tracking-tight text-purple-700"
                      >
                        {q}
                      </Chip>
                    ))}
                  </div>
                )}

                <div className="relative flex items-end gap-2 w-full bg-default-50/50 rounded-[2rem] p-2 ring-1 ring-default-200 transition-all focus-within:ring-purple-300 focus-within:bg-white shadow-inner">
                  <Textarea
                    variant="flat"
                    size="sm"
                    minRows={1}
                    maxRows={4}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        handleSend();
                      }
                    }}
                    placeholder="Ask about careers, courses, or universities..."
                    classNames={{
                      base: "flex-1",
                      input: "text-xs font-semibold placeholder:text-default-400 no-scrollbar leading-relaxed",
                      inputWrapper: "bg-transparent hover:bg-transparent shadow-none px-2",
                    }}
                  />
                  {isLoading || isTyping ? (
                    <Button
                      isIconOnly
                      radius="full"
                      color="danger"
                      variant="flat"
                      onClick={() => {
                        if (isLoading && abortControllerRef.current) {
                          abortControllerRef.current.abort();
                        } else if (isTyping) {
                          setSkipTyping(true);
                          setIsTyping(false);
                        }
                        setIsLoading(false);
                      }}
                      className="bg-red-100 text-red-600 hover:bg-red-200 active:scale-95 w-9 h-9 min-w-9 flex-shrink-0"
                    >
                      <span className="text-xl font-black">■</span>
                    </Button>
                  ) : (
                    <Button
                      isIconOnly
                      radius="full"
                      color="primary"
                      isDisabled={!message.trim()}
                      onClick={() => handleSend()}
                      className="bg-black text-white hover:scale-105 active:scale-95 disabled:bg-default-200 shadow-lg w-9 h-9 min-w-9 flex-shrink-0"
                    >
                      <span className="text-xl font-black">↗</span>
                    </Button>
                  )}
                </div>
              </CardFooter>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* --- Robot Summon FAB --- */}
      <motion.button
        whileHover={{ scale: 1.05, y: -4, rotate: -3 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(!isOpen)}
        className={`flex h-16 w-16 items-center justify-center rounded-3xl shadow-[0_25px_50px_-12px_rgba(147,51,234,0.5)] ring-4 ring-white/40 transition-all overflow-hidden relative ${isOpen ? "bg-black" : "bg-gradient-to-tr from-purple-700 to-purple-500"
          }`}
      >
        <AnimatePresence mode="wait">
          {isOpen ? (
            <motion.span
              key="close"
              initial={{ rotate: -180, opacity: 0 }}
              animate={{ rotate: 0, opacity: 1 }}
              exit={{ rotate: 180, opacity: 0 }}
              className="text-2xl font-black text-white"
            >
              ✕
            </motion.span>
          ) : (
            <motion.div
              key="open"
              initial={{ scale: 0.3, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.3, opacity: 0 }}
              className="relative h-11 w-11"
            >
              <Image
                src="/model.png"
                alt="Summon Chat"
                fill
                className="object-contain" // Robot icon as summoning button as popup
              />
            </motion.div>
          )}
        </AnimatePresence>
      </motion.button>
    </div>
  );
}
