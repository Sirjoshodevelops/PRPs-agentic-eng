# PRP AI IDE Comprehensive Workflow Guide

## Executive Summary

This guide provides comprehensive workflows for AI IDEs to leverage the PRP (Product Requirement Prompt) Framework for shipping production-ready code on the first pass. The framework follows the principle: **"PRP = PRD + curated codebase intelligence + agent/runbook"**.

## Table of Contents

1. [Quick Start Commands](#quick-start-commands)
2. [Complete Development Workflow](#complete-development-workflow)
3. [Parallel Execution Strategies](#parallel-execution-strategies)
4. [Advanced Workflows](#advanced-workflows)
5. [Command Reference](#command-reference)
6. [Best Practices](#best-practices)

---

## Quick Start Commands

### Initial Setup
```bash
# Prime Claude with project context
/prime-core

# For new projects, run onboarding analysis
/onboarding
```

### Simple Feature Implementation
```bash
# Research and create a PRP for your feature
/prp-base-create "Add user authentication with OAuth2"

# Execute the PRP
/prp-base-execute PRPs/oauth2-authentication-prp.md

# Review implementation
/review-general
```

### Rapid Development (Parallel Execution)
```bash
# For time-critical features - 4x faster with parallel research
/create-base-prp-parallel "Implement real-time notifications system"

# For hackathon-style rapid development - 25+ agents
/hackathon-prp-parallel "Build complete dashboard with analytics"
```

---

## Complete Development Workflow

### Phase 1: Research & Planning

#### 1.1 Multi-Approach Evaluation (15 Agents)
```bash
# Evaluate multiple solution approaches simultaneously
/hackathon-research "Implement caching strategy for API responses"
```
This spawns 15 agents exploring:
- Speed-First Approach (5 agents)
- Innovation-First Approach (5 agents)
- Balanced Approach (5 agents)

Output: `PRPs/research/{approach}-analysis.md` with quantitative comparisons

#### 1.2 Create Multiple PRP Variations (2-5 Agents)
```bash
# Generate different architectural approaches
/parallel-prp-creation "Build notification service" --variations 5
```
Creates PRPs optimized for:
- Performance
- Security
- Maintainability
- Rapid Development
- Enterprise Scale

#### 1.3 Standard Research & PRP Creation
```bash
# Deep research with subagent spawning
/prp-base-create "Implement GraphQL API layer"

# For TypeScript/JavaScript projects
/TS-create-base-prp "Add React component library"
```

### Phase 2: Planning & Design

#### 2.1 Transform Ideas into PRDs with Visuals
```bash
# Create comprehensive PRD with diagrams
/create-planning-parallel "E-commerce checkout flow optimization"
```
Parallel agents research:
- Market Intelligence
- Technical Feasibility
- UX/UI Best Practices
- Compliance Requirements

Output includes Mermaid diagrams for:
- System architecture
- User flows
- Data models
- Deployment strategy

#### 2.2 API Contract Definition
```bash
# Define contracts between backend and frontend
/api-contract-define "User management API"
```

#### 2.3 Task Breakdown
```bash
# Initialize detailed task list for complex features
/task-list-init "Payment processing integration"
```

### Phase 3: Validation & Preparation

#### 3.1 Pre-flight PRP Validation
```bash
# Validate PRP before execution
/prp-validate PRPs/feature-name-prp.md
```
Checks:
- Context completeness
- Dependency availability
- Risk assessment
- Auto-fix suggestions

#### 3.2 Branch Setup
```bash
# Create feature branch from latest develop
/new-dev-branch feature/notification-system
```

### Phase 4: Implementation

#### 4.1 Standard Execution
```bash
# Execute with ULTRATHINK planning
/prp-base-execute PRPs/notification-system-prp.md

# For TypeScript projects
/TS-execute-base-prp PRPs/react-components-prp.md
```

#### 4.2 Specification-Based Execution
```bash
# For clear transformation goals
/prp-spec-execute PRPs/database-migration-spec.md
```

#### 4.3 Task-Based Execution
```bash
# For focused, sequential changes
/prp-task-execute PRPs/refactoring-tasks.md
```

### Phase 5: Quality Assurance & Review

#### 5.1 Code Review
```bash
# Review all changes
/review-staged-unstaged

# General review of specific files
/review-general src/api/ src/models/

# TypeScript-specific review
/TS-review-general
```

#### 5.2 Refactoring Check
```bash
# Quick refactoring analysis
/refactor-simple
```

#### 5.3 Debug & Root Cause Analysis
```bash
# Systematic debugging
/debug-RCA "API returns 500 on user creation"
```

### Phase 6: Integration & Deployment

#### 6.1 Conflict Resolution
```bash
# Smart conflict resolution
/smart-resolver

# Specific strategy
/conflict-resolver-specific --safe --ours
```

#### 6.2 Commit & PR Creation
```bash
# Smart commit with conventional format
/smart-commit

# Create pull request
/create-pr
```

#### 6.3 Post-Implementation Analysis
```bash
# Analyze implementation results
/prp-analyze-run PRPs/notification-system-prp.md
```

---

## Parallel Execution Strategies

### Massive Parallel Development (25+ Agents)

```bash
/hackathon-prp-parallel "Build complete user dashboard with analytics"
```

**Timeline: 40 minutes total**

```
Phase 1: Specification (5 agents) - 10 min
├── Agent S1: API contracts
├── Agent S2: Data models
├── Agent S3: UI components
├── Agent S4: Security requirements
└── Agent S5: Performance targets

Phase 2: Planning (5 agents) - 10 min
├── Agent P1: Backend architecture
├── Agent P2: Frontend architecture
├── Agent P3: Database design
├── Agent P4: Testing strategy
└── Agent P5: Deployment plan

Phase 3: Implementation (10 agents) - 15 min
├── Backend (5 agents)
│   ├── Agent B1: API endpoints
│   ├── Agent B2: Business logic
│   ├── Agent B3: Database layer
│   ├── Agent B4: Authentication
│   └── Agent B5: Validation
└── Frontend (5 agents)
    ├── Agent F1: Components
    ├── Agent F2: State management
    ├── Agent F3: API integration
    ├── Agent F4: Styling
    └── Agent F5: Routing

Phase 4: Integration (2 agents) - 3 min
├── Agent I1: Backend-Frontend integration
└── Agent I2: Third-party services

Phase 5: Quality Assurance (3 agents) - 2 min
├── Agent Q1: Unit tests
├── Agent Q2: Integration tests
└── Agent Q3: Performance tests
```

### Research Parallelization (4 Agents)

```bash
/create-base-prp-parallel "Implement caching layer"
```

```
Parallel Research Agents:
├── Agent 1: Codebase Analysis
│   └── Pattern extraction, existing infrastructure
├── Agent 2: External Research
│   └── Best practices, library comparisons
├── Agent 3: Testing Strategy
│   └── Test patterns, coverage requirements
└── Agent 4: Documentation
    └── Integration guides, API references
```

### Multi-Option Evaluation (15 Agents)

```bash
/hackathon-research "Design authentication system"
```

```
Approach Evaluation:
├── Speed-First (5 agents)
│   ├── Technical feasibility
│   ├── Implementation speed
│   ├── Risk assessment
│   ├── Resource requirements
│   └── Success criteria
├── Innovation-First (5 agents)
│   └── [Same structure]
└── Balanced (5 agents)
    └── [Same structure]
```

---

## Advanced Workflows

### Workflow 1: Zero-to-Production in 2 Hours

```bash
# Step 1: Parallel research (15 min)
/hackathon-research "Build real-time collaboration feature"

# Step 2: Select best approach and create PRP (10 min)
/create-base-prp-parallel "Real-time collaboration using WebSockets"

# Step 3: Validate PRP (5 min)
/prp-validate PRPs/realtime-collab-prp.md

# Step 4: Massive parallel implementation (40 min)
/hackathon-prp-parallel "Execute real-time collaboration PRP"

# Step 5: Integration testing (20 min)
# Run validation commands from PRP

# Step 6: Review and refine (20 min)
/review-general
/refactor-simple

# Step 7: Create PR (10 min)
/smart-commit
/create-pr
```

### Workflow 2: Complex Refactoring

```bash
# Step 1: Analyze current state
/onboarding

# Step 2: Create refactoring PRP with multiple approaches
/parallel-prp-creation "Refactor monolith to microservices" --variations 3

# Step 3: Create detailed task list
/prp-task-create "Microservices migration tasks"

# Step 4: Execute incrementally
/prp-task-execute PRPs/microservices-tasks.md

# Step 5: Validate each phase
/review-staged-unstaged
```

### Workflow 3: Rapid Prototyping

```bash
# Step 1: User story to implementation plan
/user-story-rapid "As a user, I want to export my data in multiple formats"

# Step 2: API contract first
/api-contract-define "Data export API"

# Step 3: Parallel frontend/backend development
/hackathon-prp-parallel "Implement data export feature"

# Step 4: Quick iteration
/debug-RCA "Fix any issues"
/smart-commit
```

---

## Command Reference

### PRP Commands
| Command | Purpose | Execution Time | Agents |
|---------|---------|----------------|--------|
| `/prp-base-create` | Standard PRP creation | 10-15 min | 1 + subagents |
| `/create-base-prp-parallel` | Parallel PRP creation | 5-7 min | 4 |
| `/prp-base-execute` | Execute PRP | Varies | 1 |
| `/hackathon-prp-parallel` | Massive parallel execution | 40 min | 25+ |
| `/prp-validate` | Pre-flight validation | 2-3 min | 1 |
| `/prp-analyze-run` | Post-execution analysis | 5 min | 1 |

### Research Commands
| Command | Purpose | Execution Time | Agents |
|---------|---------|----------------|--------|
| `/hackathon-research` | Multi-approach evaluation | 15 min | 15 |
| `/parallel-prp-creation` | Create PRP variations | 10 min | 2-5 |
| `/create-planning-parallel` | PRD with diagrams | 10 min | 4 |

### Development Commands
| Command | Purpose | Best For |
|---------|---------|----------|
| `/prime-core` | Load project context | Session start |
| `/onboarding` | Project analysis | New projects |
| `/debug-RCA` | Root cause analysis | Bug fixing |
| `/smart-commit` | Intelligent commits | Clean history |

---

## Best Practices

### 1. Context Loading Strategy
```bash
# Always start with
/prime-core

# For complex features, research first
/hackathon-research "feature description"

# Select best approach from research
/create-base-prp-parallel "selected approach"
```

### 2. Parallel Execution Rules
- **Independence**: Each agent must work autonomously
- **Output Isolation**: Unique file paths prevent conflicts
- **Time Boxing**: Strict limits ensure predictable completion
- **Phase Gates**: Validate before proceeding

### 3. Validation Hierarchy
```bash
# Level 1: Syntax (always first)
ruff check --fix && mypy .

# Level 2: Unit Tests
pytest tests/ -v

# Level 3: Integration
# API calls, end-to-end tests

# Level 4: Creative validation
# Performance, security, load testing
```

### 4. Error Recovery
```bash
# If PRP execution fails
/prp-validate PRPs/failed-prp.md  # Identify issues
/debug-RCA "specific error"        # Root cause analysis
# Fix PRP and re-execute
```

### 5. Progressive Enhancement
```bash
# Start simple
/prp-base-create "basic feature"

# Validate works
/prp-base-execute PRPs/basic-feature.md

# Then enhance
/prp-task-create "enhancement tasks"
```

### 6. Emergency Protocols
- **Timeout Management**: Each phase has fallback strategies
- **Partial Completion**: Proceed with available results
- **Graceful Degradation**: Skip non-critical agents if behind schedule

---

## Conclusion

The PRP Framework with parallel execution capabilities enables AI IDEs to:
- Ship production-ready code 4x faster through parallelization
- Maintain high quality through comprehensive validation
- Reduce implementation failures through context-rich PRPs
- Scale from simple features to complex system redesigns

Remember: **Context is King** - The more comprehensive your PRPs, the higher your success rate.

---

*PRP Framework v2.0 | AI-First Development | One-Pass Success*