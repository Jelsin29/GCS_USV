# Skill Registry

**Delegator use only.** Any agent that launches sub-agents reads this registry to resolve compact rules, then injects them directly into sub-agent prompts. Sub-agents do NOT read this registry or individual SKILL.md files.

See `_shared/skill-resolver.md` for the full resolution protocol.

## User Skills

| Trigger | Skill | Path |
|---------|-------|------|
| Writing Rust code, reviewing Rust PRs, or making architectural decisions in Rust projects | rust-best-practices | ~/.config/opencode/skills/rust-best-practices/SKILL.md |
| CleanRoom orchestrator launches you to generate tests | cr-test | ~/.config/opencode/skills/cr-test/SKILL.md |
| CleanRoom orchestrator launches you to verify the implementation | cr-verify | ~/.config/opencode/skills/cr-verify/SKILL.md |
| CleanRoom orchestrator launches you to implement supporting tasks | cr-implement-b | ~/.config/opencode/skills/cr-implement-b/SKILL.md |
| CleanRoom orchestrator launches you to implement core tasks | cr-implement-a | ~/.config/opencode/skills/cr-implement-a/SKILL.md |
| CleanRoom orchestrator launches you to reconcile Plan A and Plan B | cr-reconcile | ~/.config/opencode/skills/cr-reconcile/SKILL.md |
| CleanRoom orchestrator launches you to challenge the primary plan | cr-plan-b | ~/.config/opencode/skills/cr-plan-b/SKILL.md |
| CleanRoom orchestrator launches you to create the primary implementation plan | cr-plan-a | ~/.config/opencode/skills/cr-plan-a/SKILL.md |
| CleanRoom orchestrator launches you to normalize analyzer outputs | cr-normalize | ~/.config/opencode/skills/cr-normalize/SKILL.md |
| CleanRoom orchestrator launches you to perform secondary analysis | cr-analyze-b | ~/.config/opencode/skills/cr-analyze-b/SKILL.md |
| CleanRoom orchestrator launches you to perform primary analysis | cr-analyze-a | ~/.config/opencode/skills/cr-analyze-a/SKILL.md |
| Creating a GitHub issue, reporting a bug, or requesting a feature | issue-creation | ~/.config/opencode/skills/issue-creation/SKILL.md |
| Creating a pull request, opening a PR, or preparing changes for review | branch-pr | ~/.config/opencode/skills/branch-pr/SKILL.md |
| Styling with Tailwind - cn(), theme variables, no var() in className | tailwind-4 | ~/.config/opencode/skills/tailwind-4/SKILL.md |
| Writing TypeScript code - types, interfaces, generics | typescript | ~/.config/opencode/skills/typescript/SKILL.md |
| Building a presentation, slide deck, course material, stream web, or talk slides | stream-deck | ~/.config/opencode/skills/stream-deck/SKILL.md |
| Reviewing technical exercises, code assessments, candidate submissions, or take-home tests | technical-review | ~/.config/opencode/skills/technical-review/SKILL.md |
| User asks to create a new skill, add agent instructions, or document patterns for AI | skill-creator | ~/.config/opencode/skills/skill-creator/SKILL.md |
| Using Zod for validation - breaking changes from v3 | zod-4 | ~/.config/opencode/skills/zod-4/SKILL.md |
| Managing React state with Zustand | zustand-5 | ~/.config/opencode/skills/zustand-5/SKILL.md |
| Writing E2E tests - Page Objects, selectors, MCP workflow | playwright | ~/.config/opencode/skills/playwright/SKILL.md |
| Writing Angular components, services, templates, or making architectural decisions | scope-rule-architect-angular | ~/.config/opencode/skills/angular/SKILL.md |
| Writing Go tests, using teatest, or adding test coverage | go-testing | ~/.config/opencode/skills/go-testing/SKILL.md |
| User says "judgment day", "review adversarial", "dual review", "juzgar" | judgment-day | ~/.config/opencode/skills/judgment-day/SKILL.md |
| Writing Python tests - fixtures, mocking, markers | pytest | ~/.config/opencode/skills/pytest/SKILL.md |
| Writing React components - no useMemo/useCallback needed | react-19 | ~/.config/opencode/skills/react-19/SKILL.md |
| Building REST APIs with Django - ViewSets, Serializers, Filters | django-drf | ~/.config/opencode/skills/django-drf/SKILL.md |
| User wants to review PRs, analyze issues, or audit PR/issue backlog | pr-review | ~/.config/opencode/skills/pr-review/SKILL.md |
| Working with Next.js - routing, Server Actions, data fetching | nextjs-15 | ~/.config/opencode/skills/nextjs-15/SKILL.md |
| User asks to create a Jira task, ticket, or issue | jira-task | ~/.config/opencode/skills/jira-task/SKILL.md |
| Writing C# code, .NET APIs, or Entity Framework models | dotnet | ~/.config/opencode/skills/dotnet/SKILL.md |
| User asks to release, bump version, update homebrew, or publish a new version | homebrew-release | ~/.config/opencode/skills/homebrew-release/SKILL.md |
| User asks to create an epic, large feature, or multi-task initiative | jira-epic | ~/.config/opencode/skills/jira-epic/SKILL.md |
| Building AI chat features - breaking changes from v4 | ai-sdk-5 | ~/.config/opencode/skills/ai-sdk-5/SKILL.md |
| User asks to commit, push, create branches, or manage PRs | git-flow | ~/.claude/skills/git-flow/SKILL.md |
| Starting a new SDD change, user says "new feature", or before sdd-apply | git-worktrees | ~/.claude/skills/git-worktrees/SKILL.md |
| Agent is about to declare a task complete, says "done"/"finished", or before creating a PR | verification-before-completion | ~/.claude/skills/verification-before-completion/SKILL.md |
| User reports a bug, tests fail, or sub-agent encounters errors during sdd-apply | systematic-debugging | ~/.claude/skills/systematic-debugging/SKILL.md |
| User describes a new project idea with no existing codebase | project-brainstorming | ~/.claude/skills/project-brainstorming/SKILL.md |

## Compact Rules

### rust-best-practices
- Use `Self` in impl blocks, NOT the type name; exception: don't use `Self::AssociatedType` for construction
- Structs: populate fields in declaration order with let bindings matching field order; all fields or none
- Scope `let mut` tightly — use blocks; prefer functional style (`.filter().count()`) over imperative mutation
- Library crates: concrete error types with `thiserror`, NEVER `Box<dyn Error>` or `anyhow`
- `.unwrap()` only where programmer is sole error source; replace with `?`, `.ok_or()`, `.expect()`
- Imports: 3 blocks ordered `std` → third-party → `crate/self/super`; no `*` imports (except `super::*` in tests)
- `mod.rs` contains ONLY module structure (pub mod, mod, pub use); no implementations; prefer `foo/mod.rs` over `foo.rs`
- Ordering: `impl MyType` → `unsafe impl StdTrait` → `impl StdTrait` → `impl MyTrait` → `impl 3rdParty`
- Naming: single-letter generics (`T`, `K`, `V`); lifetimes from reference (`'cursor`), never `'a`
- All new code MUST pass `cargo fmt` and `cargo clippy` (including `--tests` and `--all-features`)

### cr-test
- Test BEHAVIOR, not implementation — tests should pass regardless of HOW code works internally
- Never import or reference the original source system in tests
- Every requirement from normalized spec needs at least ONE test (happy path, edge cases, integration, stress)
- Use project's existing test framework; return envelope per `_shared/sdd-phase-common.md` plus contamination_assessment
- Size budget: under 600 words for report

### cr-verify
- ONLY stage (besides analyzers) that reads original source — only for COMPARISON
- Passing tests with high contamination is NOT acceptable — both must pass
- Contamination verdicts: `clean`, `acceptable`, `concerning`, `contaminated` (automatic CRITICAL on any module)
- CRITICAL issues block archiving; size budget: under 1200 words

### cr-implement-b
- Same contamination rules as Worker A — never read the original source
- Coordinate with Worker A's interfaces; supporting code should be SIMPLE and CLEAR
- If design is incomplete or ambiguous, STOP and report back — do not guess
- Mark tasks complete as you go (`- [x]`)

### cr-implement-a
- MUST NOT read original source — implement from reconciled design ONLY
- MUST NOT read raw analyses or normalized requirements — only the reconciled design
- Follow reconciled architecture decisions — do not freelance a different approach
- If design is incomplete/ambiguous, STOP and report back — do not guess

### cr-reconcile
- MUST NOT read original source or raw analyses
- Every resolution MUST have a rationale — no silent choices
- Worker A gets logic-heavy tasks; Worker B gets throughput, boilerplate, supporting tasks
- Contamination concerns from Plan B's critique MUST be addressed explicitly

### cr-plan-b
- MUST NOT read Plan A or original source — independence is critical
- Goal is DIVERSITY of approach, not necessarily "better"
- Be honest about own plan's weaknesses — reconciler needs that info
- Contamination critique is MOST VALUABLE output

### cr-plan-a
- MUST NOT read original source, raw analyses, or anything outside normalized requirements
- Design from FIRST PRINCIPLES — do not reverse-engineer original architecture
- If a requirement's language implies a specific pattern, choose a DIFFERENT valid approach
- Every architecture decision MUST have a rationale

### cr-normalize
- NEVER pass raw analysis text — everything must be converted to canonical schema (REQ-NNN, pre/postconditions, observables, error_cases, confidence, contamination_risk)
- Strip stylistic details, metaphors, model-specific language
- If analyzers disagree, include BOTH interpretations and flag the disagreement
- Requirements with `contamination_risk: high` must include rewritten abstract version

### cr-analyze-b
- Same contamination rules as Analyzer A — behavior over implementation
- MUST NOT read Analyzer A's output — independence is critical
- Flag requirements with low confidence — most valuable for normalizer to cross-reference

### cr-analyze-a
- Describe BEHAVIOR, not implementation — "system validates email format" not "regex checks emails"
- Never copy code snippets into analysis — paraphrase behavior
- Flag areas uncertain with confidence: low
- Return: System Purpose, External Interfaces, Behavioral Contracts, State Transitions, Non-Functional, Contamination Self-Check

### issue-creation
- Blank issues are disabled — MUST use a template (bug report or feature request)
- Every issue gets `status:needs-review` automatically on creation
- Maintainer MUST add `status:approved` before any PR can be opened
- Questions go to Discussions, not issues
- Search existing issues for duplicates before creating

### branch-pr
- Every PR MUST link an approved issue — no exceptions
- Every PR MUST have exactly one `type:*` label
- Branch names: `^(feat|fix|chore|docs|style|refactor|perf|test|build|ci|revert)/[a-z0-9._-]+$`
- Commits: conventional commits `type(scope): description`; no `Co-Authored-By` trailers
- PR body must include: Linked Issue (`Closes #N`), PR Type, Summary, Changes Table, Test Plan, Contributor Checklist

### tailwind-4
- NEVER use `var()` in className — use Tailwind semantic classes (`bg-primary`, not `bg-[var(--color-primary)]`)
- NEVER use hex colors in className — use Tailwind color classes (`text-white`, not `text-[#ffffff]`)
- `cn()` only for conditional/merged classes; static classes use plain `className="..."`
- Dynamic values → `style={{ width: `${x}%` }}`; chart constants with `var()` ONLY for library props

### typescript
- Const types pattern: create `const STATUS = {...} as const` then `type Status = (typeof STATUS)[keyof typeof STATUS]`
- Flat interfaces: one level depth, nested objects → dedicated interface; NEVER inline nested objects
- NEVER use `any` — use `unknown` for truly unknown types, generics for flexible types
- Use `import type { X }` for type-only imports

### stream-deck
- Single-page HTML presentation: no frameworks, no build step, no vertical scroll (`100dvh`)
- ALL diagrams are inline SVGs — never `<img>` tags; viewBox `"0 0 520 360"`
- Gentleman Kanagawa Blur palette: use EXACT colors; min contrast ratio 4:1 against `#1c212c`
- Filter IDs prefixed with `s{slideIndex}-` to avoid conflicts
- NO CSS gradients — use solid colors + shadows + blur for depth
- When inserting slides, re-index downstream from HIGHEST to LOWEST

### technical-review
- 6 evaluation factors always: Styling, Technical expertise, Code Quality, Go beyond, Detailed explanations, Other
- Score each 0-10 with specific evidence; check red flags: secrets, no tests, copy-paste, security gaps
- Output as Markdown table per candidate; end with comparative summary if multiple

### skill-creator
- Create skill when pattern is reusable and AI needs guidance; DON'T for trivial or one-off patterns
- Structure: `skills/{name}/SKILL.md` + optional `assets/` and `references/`
- Frontmatter required: name, description (with trigger), license (Apache-2.0), author (gentleman-programming), version
- `references/` points to LOCAL files, not web URLs; no Keywords section (agent searches frontmatter)

### zod-4
- Breaking changes: `z.string().email()` → `z.email()`; `z.string().nonempty()` → `z.string().min(1)`
- Error param changed from `message` to `error`: `z.string({ error: "Must be string" })`
- Top-level validators: `z.email()`, `z.uuid()`, `z.url()`
- Discriminated unions: `z.discriminatedUnion("status", [...])`; use `z.coerce.number()` for coercion

### zustand-5
- Basic store: `create<Type>((set) => ({...}))`; use `persist` middleware for localStorage
- Selectors: `useStore((state) => state.field)` for single fields; `useShallow` for multiple fields
- NEVER select entire store (causes re-render on ANY change)
- Slices pattern: separate slice creators, merge in `create<Store>()((...args) => ({...createSlice(...args)}))`

### playwright
- MANDATORY: If Playwright MCP available, explore page first (navigate, snapshot, interact, screenshot) before writing tests
- Selector priority: `getByRole` > `getByLabel` > `getByText` (sparingly) > `getByTestId` (last resort); NEVER CSS selectors
- File structure: all tests in one `.spec.ts` per page; page object in `-page.ts`; never split tests across files
- BasePage parent class: ALL pages extend it; check existing page objects before creating new ones
- Tags: `@critical`, `@high`, `@e2e`, `@SIGNUP-E2E-001`; test docs under 60 lines

### scope-rule-architect-angular
- ALL components standalone by default (Angular 20); use `input()`/`output()` functions, NOT decorators
- OnPush change detection; `inject()` instead of constructor injection; signals for state
- Native control flow (`@if`, `@for`, `@switch`); `@defer` for lazy loading; no `.component`/`.service` suffixes
- Scope Rule: code used by 2+ features → shared/; 1 feature → local. NO EXCEPTIONS
- Screaming Architecture: feature names describe business, not tech; structure tells what app does

### go-testing
- Table-driven tests: `tests := []struct{...}{{...}}; for _, tt := range tests { t.Run(tt.name, ...) }`
- Bubbletea: test `Model.Update()` directly with `tea.KeyMsg`; use `teatest.NewTestModel()` for full flows
- Golden files: compare `m.View()` output against `testdata/*.golden` files; update with `-update` flag
- File organization: `model_test.go`, `update_test.go`, `view_test.go`, `teatest_test.go`, `testdata/`

### judgment-day
- Orchestrator NEVER reviews code — only launches judges, reads results, synthesizes
- Launch TWO sub-agents via `delegate` (async, parallel); neither knows about the other
- Verdict categories: Confirmed (both found), Suspect A/B (one found), Contradiction (disagree)
- Max 2 fix iterations; on third failure → ESCALATED with full history; always resolve skills from registry first

### pytest
- Class-based tests: `class TestUserService: def test_create_user_success(self):`
- Fixtures with `@pytest.fixture`; teardown via `yield`; scopes: module, class, session
- `conftest.py` for shared fixtures; patch target path: `with patch("services.payment.stripe_client")`
- `@pytest.mark.parametrize("input,expected", [(...), (...)]); markers: `@pytest.mark.slow`, `@pytest.mark.skip`

### react-19
- No `useMemo`/`useCallback` — React Compiler handles optimization; NEVER `import React from "react"`
- Server Components by default; add `"use client"` only for useState/useEffect/event handlers/browser APIs
- `use()` hook for promises and conditional context; `ref` is a regular prop — no `forwardRef`
- Actions: `useActionState` for form mutations with pending state; `"use server"` for server actions

### django-drf
- ViewSet: `ModelViewSet` with `queryset`, `serializer_class`, `filterset_class`; `@action` for custom endpoints
- Separate serializers per action: read (SerializerMethodField), create (write_only password), update
- Filters: `django_filters.FilterSet` with `lookup_expr`; permissions: custom `BasePermission` classes
- Testing: `APIClient` + `force_authenticate`; `@pytest.mark.django_db`; `status.HTTP_201_CREATED`

### pr-review
- Always use when user mentions PR review — handles FULL flow: listing → analyzing → reviewing
- Read current codebase BEFORE reviewing diffs; check for conflicts between open PRs
- Red flags (DO NOT MERGE): test/debug files, unused vars, duplication, hardcoded secrets
- Reply in same language as author; merge order: small independent PRs first, large refactors last

### nextjs-15
- App Router: `page.tsx`, `layout.tsx`, `loading.tsx`, `error.tsx`, `not-found.tsx`; route groups `(auth)/`
- Server Components by default; Server Actions with `"use server"` + `revalidatePath` + `redirect`
- Parallel fetch: `Promise.all([getUsers(), getPosts()])`; streaming with `<Suspense fallback={...}>`
- `import "server-only"` to prevent client import; middleware at root level with `matcher` config

### jira-task
- Title format: `[TYPE] Brief description (components)` — types: BUG, FEATURE, ENHANCEMENT, REFACTOR, DOCS, CHORE
- Multi-component work → separate tasks per component (API, UI, SDK)
- Features: parent task (user-facing) + child tasks (technical per component); Bugs: sibling tasks
- Description: Current State + Expected State; Acceptance Criteria must be specific and testable

### dotnet
- Minimal APIs REQUIRED for new endpoints: `TypedResults.Ok()`, `TypedResults.NotFound()`, group with `MapGroup()`
- Primary constructors for DI: `public class OrderService(AppDbContext db, ILogger<OrderService> logger)`
- Clean Architecture: Domain → Application (Commands/Queries/Dtos) → Infrastructure (Persistence) → WebApi
- EF Core: Fluent API (`IEntityTypeConfiguration`), records for DTOs, Result pattern instead of exceptions

### homebrew-release
- Gentleman.Dots: build binaries for 4 platforms (darwin-amd64/arm64, linux-amd64/arm64), tag `v{VERSION}`
- GGA: tarball from tag `V{VERSION}`; compute SHA256 with `curl | shasum -a 256`
- Update formula in both repo AND homebrew-tap; commit message: `chore(homebrew): bump version`

### jira-epic
- Title: `[EPIC] Feature Name`; sections: Feature Overview, Requirements, Technical Considerations, Implementation Checklist
- Include Mermaid diagrams (architecture, data flow, state, ER); Figma links at top
- After epic, generate tasks with `jira-task` — task names from epic checklist items
- MCP: `customfield_10359` (Team) REQUIRED; `customfield_10363` (Work Item Description) uses Jira Wiki markup

### ai-sdk-5
- Breaking: `import { useChat } from "ai"` → `import { useChat } from "@ai-sdk/react"`; `handleSubmit` → `sendMessage`
- `message.content` (string) → `message.parts` (array of `{type: "text"|"image"|"tool-call"|"tool-result"}`
- Transport: `new DefaultChatTransport({ api: "/api/chat" })`; server: `streamText()` + `toDataStreamResponse()`
- Tools: `tool({ description, parameters: z.object({...}), execute })` inside `streamText({ tools: {...} })`

### git-flow
- 3-level branching: `master` → `feature/{name}` (epic) → `feature/{name}/setup` (integration) → `{name}/{sub}` (sub-feature)
- Merge flow bottom-up: sub-feature → integration → epic → master; NEVER force push or push to master
- Conventional commits; NEVER `git add .` — stage specific files; NEVER commit .env or secrets
- MANDATORY approval gates before push AND before PR creation — show user details, wait for explicit OK

### git-worktrees
- Create worktrees OUTSIDE project directory: `../<project-name>-<branch-name>`; NEVER inside existing project
- Check git version (>= 2.5); list existing worktrees; ensure clean working directory before creating
- Verify baseline tests pass in new worktree before starting work; save active worktree state to Engram
- Clean up after merging: `git worktree remove` + `git worktree prune`

### verification-before-completion
- HARD-GATE: cannot declare completion without showing actual test output — "it should work" is NOT evidence
- Checklist (all items with SHOWN evidence): tests pass, requirement met, no regressions, build clean, lint clean, edge cases, no debug code
- Any FAIL → fix before completing; SKIP acceptable only with documented reason
- Search for leftover debug: console.log, print(), debugger, TODO/FIXME/HACK, commented-out code

### systematic-debugging
- 4 mandatory sequential phases: Gather Evidence → Isolate Root Cause → Fix with Evidence → Verify and Harden
- HARD-GATE: no fixes before Phase 1 complete; must reproduce issue before analyzing
- Phase 3: write failing test FIRST (TDD for bugfixes), then minimal fix; if fix >20 lines, reconsider root cause
- Phase 4: check for similar patterns elsewhere; add validation at boundary where bad data entered

### project-brainstorming
- ONLY for new projects with no existing codebase — NOT for features in existing projects (that's sdd-explore)
- HARD-GATE: do NOT write code, scaffold, or create files; ONLY output is project brief document
- ONE question per message; prefer multiple-choice; apply YAGNI ruthlessly to features
- After brief, hand off to SDD pipeline — no direct implementation; scope check if project is too large

## Project Conventions

| File | Path | Notes |
|------|------|-------|
| — | — | No convention files found (no AGENTS.md, CLAUDE.md, .cursorrules, GEMINI.md, or copilot-instructions.md) |
