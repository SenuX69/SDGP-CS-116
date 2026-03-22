"use client";

import { useState, useRef, useCallback } from "react";

const API_BASE = "http://localhost:8000";

// Skill Pill
function Pill({ label, type }) {
  const colors = {
    matched: { bg: "#ecfdf5", text: "#065f46", border: "#6ee7b7" },
    missing: { bg: "#fff1f2", text: "#9f1239", border: "#fda4af" },
    neutral: { bg: "#f9fafb", text: "#374151", border: "#e5e7eb" },
  };
  const c = colors[type] || colors.neutral;
  return (
    <span
      style={{
        display: "inline-block",
        padding: "3px 12px",
        borderRadius: "999px",
        fontSize: "0.78rem",
        fontWeight: 500,
        background: c.bg,
        color: c.text,
        border: `1px solid ${c.border}`,
        margin: "3px",
      }}
    >
      {label}
    </span>
  );
}

// Experience Card
function ExpCard({ entry, index }) {
  return (
    <div
      style={{
        background: "#f9fafb",
        border: "1px solid #e5e7eb",
        borderRadius: 12,
        padding: "14px 18px",
        marginBottom: 10,
        borderLeft: "3px solid #06b6d4",
        animationDelay: `${index * 0.08}s`,
      }}
      className="card-fadein"
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          flexWrap: "wrap",
          gap: 4,
        }}
      >
        <div>
          {entry.role && (
            <p style={{ fontWeight: 600, color: "#111827", fontSize: "0.92rem" }}>
              {entry.role}
            </p>
          )}
          {entry.company && <p style={{ color: "#6b7280", fontSize: "0.83rem" }}>{entry.company}</p>}
        </div>
        {entry.duration && (
          <span
            style={{
              fontSize: "0.75rem",
              color: "#06b6d4",
              background: "#ecfeff",
              border: "1px solid #a5f3fc",
              borderRadius: 999,
              padding: "2px 10px",
              whiteSpace: "nowrap",
            }}
          >
            {entry.duration}
          </span>
        )}
      </div>
      {entry.description && (
        <p style={{ marginTop: 8, fontSize: "0.82rem", color: "#4b5563", lineHeight: 1.6 }}>
          {entry.description}
        </p>
      )}
    </div>
  );
}

// Education Card
function EduCard({ entry, index }) {
  return (
    <div
      style={{
        background: "#f9fafb",
        border: "1px solid #e5e7eb",
        borderRadius: 12,
        padding: "14px 18px",
        marginBottom: 10,
        borderLeft: "3px solid #8b5cf6",
      }}
      className="card-fadein"
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          flexWrap: "wrap",
          gap: 4,
        }}
      >
        <div>
          {entry.degree && (
            <p style={{ fontWeight: 600, color: "#111827", fontSize: "0.92rem" }}>
              {entry.degree}
            </p>
          )}
          {entry.institution && <p style={{ color: "#6b7280", fontSize: "0.83rem" }}>{entry.institution}</p>}
        </div>
        {entry.duration && (
          <span
            style={{
              fontSize: "0.75rem",
              color: "#7c3aed",
              background: "#f5f3ff",
              border: "1px solid #c4b5fd",
              borderRadius: 999,
              padding: "2px 10px",
              whiteSpace: "nowrap",
            }}
          >
            {entry.duration}
          </span>
        )}
      </div>
    </div>
  );
}

// Section Block
function Section({ title, children, accent = "#06b6d4" }) {
  return (
    <div style={{ marginBottom: 28 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
        <div style={{ width: 4, height: 20, background: accent, borderRadius: 2 }} />
        <h3 style={{ fontWeight: 600, fontSize: "1rem", color: "#111827", margin: 0 }}>{title}</h3>
      </div>
      {children}
    </div>
  );
}

export default function ResumeScanner() {
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [tab, setTab] = useState("analysis"); // "analysis" | "parsed" | "preview"
  const inputRef = useRef(null);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) setFile(dropped);
  }, []);

  const handleScan = async () => {
    if (!file) return;
    setLoading(true);
    setResult(null);
    setError("");
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res = await fetch(`${API_BASE}/scan`, { method: "POST", body: fd });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Scan failed");
      setResult(data);
      setTab("analysis");
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!result?.filename) return;
    window.open(`${API_BASE}/download/${result.filename}`, "_blank");
  };

  const p = result?.parsed ?? {};
  const a = result?.analysis ?? null;
  const personalInfo = p.personal_info ?? {};
  const matchedSkills = Array.isArray(a?.matched_skills) ? a.matched_skills : [];
  const missingSkills = Array.isArray(a?.missing_skills) ? a.missing_skills : [];
  const suggestionList = Array.isArray(a?.suggestions) ? a.suggestions : [];

  const matchedCount = matchedSkills.length;
  const missingCount = missingSkills.length;

  return (
    <>
      {/* NAVBAR */}
      <nav className="pf-nav">
        <a className="pf-nav-brand" href="#">
          <div className="logo-mark">P</div>
          PathFinder
        </a>
        <ul className="pf-nav-links">
          {["Home", "Career Path", "Courses", "Jobs", "Mentorship", "Dashboard"].map((l) => (
            <li key={l} className={l === "Dashboard" ? "active" : ""}>
              {l}
            </li>
          ))}
        </ul>
        <div className="pf-avatar">JD</div>
      </nav>

      {/* PAGE */}
      <div className="pf-page">
        <div className="pf-header card-fadein">
          <p>Resume Tools</p>
          <h1>Resume Creation / Analysis</h1>
        </div>

        {/* UPLOAD */}
        <div
          className={`upload-zone card-fadein ${dragging ? "drag-over" : ""} ${file ? "has-file" : ""}`}
          onClick={() => inputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.docx,.doc"
            style={{ display: "none" }}
            onChange={(e) => setFile(e.target.files[0])}
          />
          <div className="upload-icon">{file ? "📄" : "☁️"}</div>
          {file ? (
            <>
              <h3>{file.name}</h3>
              <p>{(file.size / 1024).toFixed(1)} KB · Click to change</p>
            </>
          ) : (
            <>
              <h3>Drop your resume here</h3>
              <p>PDF or DOCX · Click to browse</p>
            </>
          )}
        </div>

        {/* ACTIONS */}
        <div style={{ display: "flex", gap: 12, marginTop: 16, alignItems: "center" }}>
          <button className="btn-primary" disabled={!file || loading} onClick={handleScan}>
            {loading ? (
              <>
                <div className="loading-spinner" /> Scanning…
              </>
            ) : (
              <>
                <span>🔍</span> Scan Resume
              </>
            )}
          </button>
          {file && !loading && (
            <button
              className="btn-ghost"
              onClick={() => {
                setFile(null);
                setResult(null);
                setError("");
              }}
            >
              Clear
            </button>
          )}
          {result && (
            <button className="btn-ghost" onClick={handleDownload}>
              ⬇ Download Report
            </button>
          )}
        </div>

        {/* ERROR */}
        {error && (
          <div
            style={{
              marginTop: 16,
              padding: "12px 18px",
              background: "#fff1f2",
              border: "1px solid #fda4af",
              borderRadius: 10,
              color: "#9f1239",
              fontSize: "0.85rem",
            }}
          >
            ⚠ {error}
          </div>
        )}

        {/* RESULTS */}
        {result && (
          <div className="results-grid">
            {/* LEFT — Personal info + analysis */}
            <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
              {/* Analysis highlights */}
              <div className="card card-fadein" style={{ textAlign: "center" }}>
                <p style={{ margin: "0 0 16px", fontWeight: 600, fontSize: "0.9rem", color: "#6b7280" }}>
                  Analysis Highlights
                </p>
                <p style={{ margin: "0 0 8px", fontSize: "0.85rem", color: "#374151" }}>
                  Matched Skills: <strong>{matchedCount}</strong>
                </p>
                <p style={{ margin: "0 0 20px", fontSize: "0.85rem", color: "#374151" }}>
                  Missing Skills: <strong>{missingCount}</strong>
                </p>
                <p style={{ margin: 0, fontSize: "0.8rem", color: "#9ca3af" }}>
                  Review suggestions to improve role fit and resume clarity.
                </p>
              </div>

              {/* Personal info */}
              <div className="card card-fadein">
                <p style={{ margin: "0 0 14px", fontWeight: 600, fontSize: "0.9rem", color: "#6b7280" }}>
                  Contact
                </p>
                {personalInfo.name && (
                  <div className="info-row">
                    <div className="info-icon" style={{ background: "#eff6ff" }}>
                      👤
                    </div>
                    <span style={{ fontWeight: 600 }}>{personalInfo.name}</span>
                  </div>
                )}
                {personalInfo.email && (
                  <div className="info-row">
                    <div className="info-icon" style={{ background: "#ecfeff" }}>
                      ✉
                    </div>
                    <span style={{ color: "#374151" }}>{personalInfo.email}</span>
                  </div>
                )}
                {personalInfo.phone && (
                  <div className="info-row">
                    <div className="info-icon" style={{ background: "#f0fdf4" }}>
                      📞
                    </div>
                    <span style={{ color: "#374151" }}>{personalInfo.phone}</span>
                  </div>
                )}
                {personalInfo.links?.map((l, i) => (
                  <div className="info-row" key={i}>
                    <div className="info-icon" style={{ background: "#faf5ff" }}>
                      🔗
                    </div>
                    <a
                      className="text-link"
                      href={l.startsWith("http") ? l : `https://${l}`}
                      target="_blank"
                      rel="noreferrer"
                    >
                      {l}
                    </a>
                  </div>
                ))}
              </div>
            </div>

            {/* RIGHT — Tabs */}
            <div className="card card-fadein">
              <div className="tab-row">
                {["analysis", "parsed", "preview"].map((t) => (
                  <button
                    key={t}
                    className={`tab-btn ${tab === t ? "active" : ""}`}
                    onClick={() => setTab(t)}
                  >
                    {t === "analysis" ? "📊 Analysis" : t === "parsed" ? "📋 Resume" : "📄 Raw Text"}
                  </button>
                ))}
              </div>

              {/* ANALYSIS TAB */}
              {tab === "analysis" && (
                <div>
                  {!a ? (
                    <p style={{ color: "#9ca3af", fontSize: "0.85rem", margin: 0 }}>
                      No analysis data returned. Try scanning again.
                    </p>
                  ) : (
                    <>
                      <Section title="Matched Skills" accent="#06b6d4">
                        <div>
                          {matchedSkills.length ? (
                            matchedSkills.map((s) => <Pill key={s} label={s} type="matched" />)
                          ) : (
                            <p style={{ color: "#9ca3af", fontSize: "0.83rem" }}>No required skills matched.</p>
                          )}
                        </div>
                      </Section>

                      <Section title="Missing Core Skills" accent="#ef4444">
                        <div>
                          {missingSkills.length ? (
                            missingSkills.map((s) => <Pill key={s} label={s} type="missing" />)
                          ) : (
                            <p style={{ color: "#6ee7b7", fontSize: "0.83rem" }}>✓ All core skills covered!</p>
                          )}
                        </div>
                      </Section>

                      {suggestionList.length > 0 && (
                        <Section title="Suggestions" accent="#f59e0b">
                          <div>
                            {suggestionList.map((s, i) => (
                              <div className="suggestion-item" key={i}>
                                <div className="suggestion-dot" />
                                <span>{s}</span>
                              </div>
                            ))}
                          </div>
                        </Section>
                      )}
                    </>
                  )}
                </div>
              )}

              {/* PARSED TAB */}
              {tab === "parsed" && (
                <div>
                  {p.summary && (
                    <Section title="Summary" accent="#06b6d4">
                      <p style={{ fontSize: "0.85rem", color: "#4b5563", lineHeight: 1.7, margin: 0 }}>
                        {p.summary}
                      </p>
                    </Section>
                  )}

                  {p.skills?.length > 0 && (
                    <Section title="Skills" accent="#8b5cf6">
                      <div>{p.skills.map((s) => <Pill key={s} label={s} type="neutral" />)}</div>
                    </Section>
                  )}

                  {p.experience?.length > 0 && (
                    <Section title="Experience" accent="#06b6d4">
                      {p.experience.map((e, i) => (
                        <ExpCard key={i} entry={e} index={i} />
                      ))}
                    </Section>
                  )}

                  {p.education?.length > 0 && (
                    <Section title="Education" accent="#8b5cf6">
                      {p.education.map((e, i) => (
                        <EduCard key={i} entry={e} index={i} />
                      ))}
                    </Section>
                  )}

                  {p.projects && (
                    <Section title="Projects" accent="#10b981">
                      <p
                        style={{
                          fontSize: "0.85rem",
                          color: "#4b5563",
                          lineHeight: 1.7,
                          margin: 0,
                          whiteSpace: "pre-wrap",
                        }}
                      >
                        {p.projects}
                      </p>
                    </Section>
                  )}

                  {p.certifications && (
                    <Section title="Certifications" accent="#f59e0b">
                      <p
                        style={{
                          fontSize: "0.85rem",
                          color: "#4b5563",
                          lineHeight: 1.7,
                          margin: 0,
                          whiteSpace: "pre-wrap",
                        }}
                      >
                        {p.certifications}
                      </p>
                    </Section>
                  )}

                  {p.achievements && (
                    <Section title="Achievements" accent="#ef4444">
                      <p
                        style={{
                          fontSize: "0.85rem",
                          color: "#4b5563",
                          lineHeight: 1.7,
                          margin: 0,
                          whiteSpace: "pre-wrap",
                        }}
                      >
                        {p.achievements}
                      </p>
                    </Section>
                  )}
                </div>
              )}

              {/* PREVIEW TAB */}
              {tab === "preview" && (
                <div>
                  <div className="preview-block">{result.preview}</div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* CHATBOT FAB */}
      <button className="chatbot-fab" title="Open chatbot">
        💬
      </button>
    </>
  );
}

