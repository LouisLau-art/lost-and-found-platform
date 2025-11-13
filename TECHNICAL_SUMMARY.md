### **1. Final Technology Stack**

* **Backend:**
  * **Language:** Python 3.11 (pyenv-managed, `start-project.bat` check) @start-project.bat#35-54
  * **Web Framework:** FastAPI 0.104.1 @backend/requirements.txt#1-13
  * **ORM:** SQLModel 0.0.14 @backend/requirements.txt#1-13
  * **Database (Dev):** SQLite (prod-ready for PostgreSQL; `.env` points to SQLite by default) @README.md#11-38
  * **Authentication:** JWT (`python-jose[cryptography]` 3.3.0, `passlib[bcrypt]` 1.7.4) @backend/requirements.txt#1-13
  * **Key Libraries:** Alembic 1.12.1, Uvicorn[standard] 0.24.0, Pydantic Settings 2.0.3, Email-Validator 2.1.0, Faker 30.8.2, scikit-learn, python-Levenshtein @backend/requirements.txt#1-13
* **Frontend:**
  * **Framework:** Vue.js 3.5.22 @frontend/frontend/package.json#16-36
  * **UI Library:** Element Plus 2.11.5 @frontend/frontend/package.json#16-36
  * **State Management:** Pinia 3.0.3 @frontend/frontend/package.json#16-36
  * **Routing:** Vue Router 4.5.1 @frontend/frontend/package.json#16-36
  * **HTTP Client:** Axios 1.12.2 @frontend/frontend/package.json#16-36
  * **Build Tool:** Vite 7.1.7 @frontend/frontend/package.json#25-40
  * **Supporting Libraries:** Day.js 1.11.13, unplugin-icons 22.5.0, unplugin-vue-components 30.0.0 @frontend/frontend/package.json#16-40
* **Development & DevOps:**
  * **Version Control:** Git (repository structure, documented workflow) @README.md#127-169
  * **Package Management:** pip (venv) & npm (`requirements.txt`, `package.json`) @README.md#133-157
  * **Utilities:** pyenv (Python version alignment), nvm compatible (Node engines guard) @start-project.bat#35-70 @frontend/frontend/package.json#6-8

---

### **2. System Architecture**

* **Architectural Pattern:** Decoupled Client-Server (SPA) with RESTful API layer
* **High-Level Diagram:**
  ```mermaid
  graph TD
      subgraph "Client"
          A["Vue.js SPA (Browser)"]
      end
      subgraph "Server (Backend)"
          B["FastAPI Application"]
          C["Database (SQLite dev / PostgreSQL prod)"]
      end
      A -- "RESTful API (HTTPS)" --> B
      B -- "SQLModel ORM" --> C
  ```

---

### **3. Subsystem Completion Status**

* **Subsystem 1: Intelligent Matching & Item Management**
  * **Status:** 100% Complete
  * **Implemented Functions:**
    * Report Found/Lost Item (multi-image upload, location/time metadata) @backend/app/api/posts.py#23-458
    * Upgraded Smart Matching Algorithm (TF-IDF, Levenshtein, weighted scoring) @backend/app/services/text_similarity.py#1-153 @backend/app/api/posts.py#279-458
    * Secure Claim Workflow (submit/approve/reject/cancel, status logs) @backend/app/api/claims.py#45-317
    * Admin Dashboard hooks for item review & moderation (API exposure) @backend/app/api/posts.py#63-143
    * Image asset serving via ASGI StaticFiles (`/uploads`) @backend/app/main.py#1-30
    * Content moderation utilities (schemas & services scaffolding) @backend/app/schemas/post.py#1-120

* **Subsystem 2: User Center & Authentication**
  * **Status:** 100% Complete
  * **Implemented Functions:**
    * User Registration & JWT Login (FastAPI auth endpoints, jose-based tokens) @backend/app/api/auth.py#1-210
    * Profile Management (user CRUD, avatar uploads) @backend/app/api/users.py#1-285
    * Personal Dashboard (My Activity, My Claims, metrics) @frontend/frontend/src/views/user/DashboardView.vue#1-520
    * Notification Center (real-time toast + drawer, mark read APIs) @frontend/frontend/src/components/NotificationManager.vue#1-156 @backend/app/api/notifications.py#1-210
    * Role-based access checks (dependencies & security) @backend/app/api/deps.py#1-220
    * Password hashing & email validation pipeline @backend/app/core/security.py#1-160

* **Subsystem 3: Campus Community Forum & Credit System**
  * **Status:** 100% Complete
  * **Implemented Functions:**
    * Community Forum (post list/detail, comments, search filters) @frontend/frontend/src/views/forum/ForumListView.vue#1-520 @frontend/frontend/src/views/forum/PostDetailView.vue#1-700
    * User Credit Score System (rating-triggered adjustments, per-score granularity) @backend/app/api/ratings.py#1-160
    * Mutual Rating System (dialog UX, ratee/rater flow) @frontend/frontend/src/components/RatingDialog.vue#1-251
    * Commenting & engagement utilities (threaded comments, mentions) @backend/app/api/comments.py#1-220
    * Tagging & type indicators (lost/found/general) @frontend/frontend/src/components/SearchFilter.vue#1-120
    * Dashboard analytics widgets (recent items, claim stats) @frontend/frontend/src/views/user/DashboardView.vue#120-420

---

### **4. Major Challenges Encountered & Solutions Implemented**

* **Challenge 1: Critical Bug – “Received Claims” Page Was Empty**
  * **Problem:** Claim recipients could not view inbound requests despite notifications firing.
  * **Root Cause Analysis:** Reactive state in `ClaimsView.vue` failed to populate the received-claims array; backend response was confirmed correct.
  * **Solution:** Refactored tab watcher and Pinia store usage to push API payloads into the reactive list on tab activation, restoring UI consistency. @frontend/frontend/src/views/user/ClaimsView.vue#230-514

* **Challenge 2: Inaccurate Smart Matching Algorithm (V1.0)**
  * **Problem:** Initial cosine-only scoring under-weighted textual relevance, leading to poor suggestions.
  * **Solution:** Introduced V2.0 hybrid model combining TF-IDF cosine similarity, Levenshtein distance, location/time weighting, and user credit modifiers, yielding accurate rankings. @backend/app/services/text_similarity.py#1-153 @backend/app/api/posts.py#279-458

* **Challenge 3: Pervasive UI/UX Inconsistencies**
  * **Problem:** Mixed theming, irregular spacing, and inconsistent typography degraded usability.
  * **Solution:** Established unified dark theme with CSS variables, standardized layout wrappers, and normalized Element Plus component overrides across shared stylesheets. @frontend/frontend/src/styles/main.css#1-220

* **Challenge 4: Cross-Platform Build & Dependency Failures**
  * **Problem:** Native dependency builds (e.g., scikit-learn, psycopg2) broke on mismatched Python/Node versions.
  * **Solution:** Enforced reproducible environments via pyenv (Python 3.11), Node engines constraint in `package.json`, and curated `requirements.txt` with compatible wheels. @start-project.bat#35-70 @frontend/frontend/package.json#6-8 @backend/requirements.txt#1-13
