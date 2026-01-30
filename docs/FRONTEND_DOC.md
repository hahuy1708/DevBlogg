# PROJECT CONTEXT & TECHNOLOGY STACK

**Context:** Build a CMS (Content Management System) inspired by dev.to, viblo, medium,... The goal is to create an environment for developers to write and share knowledge (technical writing), discuss, and store great articles. The system needs to provide a great user experience, smooth interactions, and a modern look and feel.

## 1. Project Overview
- **Name**: DevBlogg
- **Type**: Developer Blogging Platform (CMS).
- **Structure**: Monorepo.

## 2. Tech Stack
- **Framework**: Next.js  (App Router, SSR, API routes)
- **UI Styling**: TailwindCSS (utility-first CSS framework)
- **State Management**: React hooks (useState, useReducer, useContext)
- **Icons & UI Enhancements**: Lucide React

## 3. Project Structure
The frontend MUST follow these rules strictly:

### A. The Data Layer (services/)
- NEVER call axios or fetch directly inside Components or Pages.
- All API calls must be encapsulated in a service file (e.g., services/postService.ts).
- Handle axios response data unwrapping here.

### B. The Logic Layer (hooks/)
- **Separation of Logic**: UI components should not contain complex logic (useEffect, huge useState blocks).

- Create a custom hook (e.g., useLogin.ts, usePosts.ts) to handle:
    - Calling Services.
    - Managing Loading/Error states.
    - Form handling logic.
    - Data transformation.
- Hooks should return data and handler functions (e.g., { posts, loading, createPost }).

### C. The UI Layer (components/)
- **Dumb/Presentational**: Components should primarily receive props and emit events (callbacks).
- Keep them pure when possible. They display data provided by Hooks or Pages.
- Use Tailwind CSS for styling.

### D. The Composition Layer (app/)
- **Page.tsx**: Acts as the "Controller". It connects the Hook to the Component.
- **Server Components**: Use them for initial data fetching (SEO) if possible, then pass data to Client Components.
- **Client Components**: Use 'use client' only when interaction (hooks) is needed.

### E. Workflow for Building Features
When build a feature, follow these steps in order:

1. Define Types: Create interfaces in lib/types/.

2. Create Service: Write API functions in services/[feature]Service.ts.

3. Create Hook: Implement business logic in hooks/use[Feature].ts.

4. Create Components: Build UI in components/[feature]/.

5. Assemble: Implement the route in app/[feature]/page.tsx.

