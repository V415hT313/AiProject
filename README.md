# 🤖 R2D2

**Your own AI-powered second brain — local-first, private, and built to actually get things done.**

R2D2 is a self-hosted personal workspace: a document-grounded AI chatbot, a to-do list, notes
with live markdown preview, and a habit/expense tracker, running on your own machine, on your
own data, for as many accounts as you need.

---

## ✨ Features

- 🔐 **Multi-user accounts** - register/log in, every user's todos, notes, tracker rows, uploaded
  documents, and chat/RAG data are fully isolated from every other user's.
- 🔑 **Forgot / reset password** - request a reset link by email; it's a real, working email sent
  via Gmail SMTP, with a time-limited single-use link.
- 💬 **AI Chatbot, grounded in your own documents** - ask questions about documents you upload;
  answers come from Retrieval-Augmented Generation, streamed token-by-token, with source
  citations. Attach a PDF/TXT/MD file directly from the chat box to add it to that chat's
  knowledge base - **documents are scoped per chat**, so a file you attach in one conversation is
  never visible or searchable from another; start a new chat and it has zero access to any other
  chat's documents. Conversations are saved as chat history, pick up an old chat from the
  sidebar and it continues with full context, or start fresh with "New Chat." A "Save chat as
  note" button snapshots the current conversation into your Notes (a one-time copy, not a live
  link - it won't change if you keep chatting afterward).
- ✅ **To-do List** - checkboxes, color-coded priorities (🔴 high / 🟡 medium / 🟢 low).
- 📝 **Notes** - markdown editor with a live side-by-side preview.
- 📊 **Tracker** - a spreadsheet-style grid (add/edit/delete rows inline), a Status dropdown
  (Start / In Progress / Done), a date picker, and one-click Excel export.
- 🏠 **Home dashboard** - at-a-glance stats: open todos, ingested document count, recent notes.
