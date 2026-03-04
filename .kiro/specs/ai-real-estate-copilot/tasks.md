# Implementation Plan

## Backend: LangGraph/Deep Agent Implementation

- [x] 1. Set up project structure and dependencies
  - Initialize Python project with uv (uv init)
  - Create pyproject.toml with project metadata
  - Install deepagents, langgraph, langchain packages with uv add
  - Install FastAPI and fastapi-clerk-auth packages with uv add
  - Install Amazon Nova SDK (langchain-amazon-nova) with uv add
  - Install Google Generative AI SDK for Gemini with uv add
  - Install psycopg2-binary for PostgreSQL checkpointer with uv add
  - Create requirements.txt from uv dependencies
  - Create .env file from .env.example for API keys
  - Create directory structure: src/ (agent.py, prompts.py, tools.py, models.py, main.py, guardrails.py), tests/
  - Run uv sync to create virtual environment and install dependencies
  - _Requirements: All requirements depend on proper setup_

- [x] 2. Implement core data models
  - Create Property model with all required fields (id, address, price, bedrooms, bathrooms, etc.)
  - Create SearchCriteria model with location, price range, and property type filters
  - Create PointOfInterest model for location data
  - Create LocationAnalysis model with POIs, pros, cons, and scores
  - Create PropertyReport model to structure final output
  - _Requirements: 2.1, 4.1, 5.1_
  - _Files: src/models.py_

- [x] 3. Implement Nova Web Grounding and Browser Use MCP integration
  - Configure Amazon Nova model with system_tools=["nova_grounding"] for web search
  - Initialize MultiServerMCPClient for Browser Use cloud-hosted MCP server
  - Configure MCP client with BROWSER_USE_API_KEY from environment
  - Get browser automation tools from MCP server at startup
  - Add browser_tools to property_search_agent configuration
  - Test web grounding and browser automation capabilities
  - _Requirements: 2.2, 2.3, 2.4_
  - _Files: src/agent.py_

- [x] 4. Implement Google Places location tools
  - Create google_places_geocode_tool to convert addresses to coordinates using Text Search API
  - Create google_places_nearby_tool to find POIs by category and radius using Nearby Search API
  - Implement distance calculation utility function using Haversine formula
  - Add error handling for geocoding and API failures
  - _Requirements: 4.2, 4.3, 4.4_
  - _Files: src/tools.py_

- [x] 5. Implement Property Search Sub-Agent with Nova and Browser Use
  - Define property_search_agent configuration with name, description, and system prompt
  - Write system prompt instructing agent to use Nova Web Grounding for finding listing URLs
  - Write system prompt instructing agent to use browser_task for scraping property details
  - Configure agent with present_properties_for_review_tool and browser_tools
  - Configure agent with ChatAmazonNova model with nova_grounding system tool
  - Configure interrupt_on for present_properties_for_review_tool with allowed_decisions
  - Add PropertyOutputGuardrail middleware for output validation
  - Implement logic to write each property to separate JSON file in /properties/ directory
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.7, 6.2_
  - _Files: src/agent.py, src/prompts.py, src/guardrails.py_

- [x] 6. Implement Location Analysis Sub-Agent
  - Define location_analysis_agent configuration with name, description, and system prompt
  - Write system prompt instructing agent to use Google Places tools and analyze locations
  - Configure agent with google_places_geocode_tool and google_places_nearby_tool
  - Implement logic to search for POIs in categories: restaurant, cafe, park, shopping_mall, transit_station, school, hospital, gym
  - Implement pros/cons analysis logic based on nearby amenities
  - Implement logic to write analysis to /locations/ directory
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_
  - _Files: src/agent.py, src/prompts.py_

- [x] 7. Implement Supervisor Agent with CompositeBackend
  - Create supervisor agent using create_deep_agent with Amazon Nova Premier model
  - Write comprehensive system prompt for conversation management and coordination
  - Configure agent with property_search_agent, location_analysis_agent, and interior_decorator_agent as subagents
  - Configure agent with submit_final_report_tool
  - Implement search criteria extraction from natural language
  - Configure checkpointer (MemorySaver for dev)
  - Implement CompositeBackend with StateBackend (default) and StoreBackend (/memories/)
  - Configure InMemoryStore for local development
  - Add persistent memory instructions to system prompt
  - Define SupervisorState schema with messages, todos, search_criteria, approved_properties, filesystem
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 7.1, 8.1, 8.2, 8.3, 17.1, 17.2, 17.3_
  - _Files: src/agent.py, src/prompts.py_


- [x] 8. Implement human-in-the-loop interrupt
  - Configure interrupt_on parameter for supervisor agent with "present_properties_for_review_tool" trigger
  - Implement present_properties_for_review_tool to trigger interrupt after Property Search Agent completes
  - Implement interrupt payload with property summaries and images
  - Implement resume logic to accept approved_properties input via Command
  - Implement re-search logic when properties are rejected in supervisor prompt
  - _Files: src/agent.py, src/tools.py, src/prompts.py_
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [x] 9. Implement report compilation
  - Implement logic to read property files from /properties/ directory
  - Implement logic to read location analysis files from /locations/ directory
  - Implement PropertyReport generation combining all data
  - Format report with property details, images, location analysis, pros/cons
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  - _Files: src/utils.py, src/tools.py, src/agent.py, src/prompts.py_

- [x] 10. Implement Interior Decorator Sub-Agent with external disk storage
  - Define interior_decorator_agent configuration with name, description, and system prompt
  - Write system prompt instructing agent to analyze images and generate decorated versions
  - Write system prompt with CRITICAL RULES to prevent context overflow (never read base64 data)
  - Configure agent with analyze_property_images_tool and generate_decorated_image_tool
  - Implement workflow: receive image URLs → analyze → generate decorated images → save to EXTERNAL disk
  - Update generate_decorated_image_tool to save base64 to decorated_images/ folder (external disk)
  - Update generate_decorated_image_tool to return metadata only (no base64 in response)
  - Implement logic to write METADATA ONLY to /decorations/ directory with external_disk_path
  - Update Supervisor Agent to delegate to Interior Decorator after property approval
  - Update PropertyReport model to include decorated_images field with external paths
  - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7, 15.8, 15.9_
  - _Files: src/agent.py, src/prompts.py, src/tools.py, src/models.py_

- [ ] 11. Write integration tests for LangGraph workflow
  - Write test for complete property search workflow with invoke
  - Write test for human-in-the-loop interrupt and resume
  - Write test for property rejection and re-search flow
  - Write test for error handling with invalid location
  - _Requirements: All requirements_

- [ ]* 11. Write unit tests for core utilities
  - Write test for search criteria extraction logic
  - Write test for distance calculation utility
  - _Requirements: 1.2, 4.4_

- [ ]* 12. Write trajectory tests with AgentEvals
  - Write trajectory match test for expected tool call sequence
  - Write LLM-as-judge test for agent decision quality
  - _Requirements: All requirements_

- [x] 13. Implement FastAPI server with streaming support (src/main.py)
  - Create src/main.py with FastAPI app and async lifespan
  - Implement lifespan function to initialize MCP client and supervisor at startup
  - Set up ClerkConfig with CLERK_JWKS_URL from environment
  - Create ClerkHTTPBearer guard for authentication
  - Implement POST /api/invoke endpoint with Clerk auth and interrupt handling
  - Implement POST /api/stream endpoint for Server-Sent Events progress streaming
  - Implement POST /api/stream-resume endpoint for post-review progress streaming
  - Implement POST /api/resume endpoint with Clerk auth and Command-based resume
  - Implement POST /api/state endpoint with Clerk auth using StateRequest model
  - Implement GET /api/interior-image/{property_id} endpoint for fetching decorated images
  - Import supervisor_agent from src/agent.py
  - Extract user_id from creds.decoded["sub"] for thread isolation
  - Implement extract_final_report function to build report from filesystem
  - Implement build_report_from_filesystem function with disk and message fallback
  - Implement serialize_interrupt function for JSON serialization
  - Test API endpoints locally with JWT token
  - _Requirements: 8.1, 8.2, 12.3, 12.4, 13.1, 13.2, 16.1, 16.2, 16.3, 16.4, 16.5, 16.6_

- [ ]* 14. Set up LangSmith monitoring for backend
  - Configure LangSmith API key in environment variables
  - Add tracing to supervisor agent
  - Set up error logging and alerting
  - Create dashboard for monitoring agent performance


## Frontend: Next.js with Clerk Authentication

- [x] 15. Create Next.js frontend project with Clerk authentication
  - Initialize Next.js 14+ project with TypeScript and Pages Router in frontend/ directory
  - Install @clerk/nextjs package for authentication
  - Install and configure Tailwind CSS
  - Set up project structure with frontend/src/pages, frontend/src/components, frontend/src/lib, frontend/src/styles directories
  - Configure environment variables: NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY, CLERK_SECRET_KEY, CLERK_JWKS_URL
  - Note: API calls go to /api (same domain, no separate API_URL needed)
  - _Requirements: 10.1, 10.2, 10.3, 13.5, 14.1_


- [x] 16. Set up Clerk authentication and route protection
  - Wrap application with ClerkProvider in frontend/src/pages/_app.tsx
  - Create frontend/src/middleware.ts with clerkMiddleware for route protection
  - Define protected routes: /agent and /profile
  - Add getServerSideProps to protected pages for server-side auth checks
  - Configure redirect URLs for sign-in and sign-up flows
  - Test authentication flow and route protection
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 13.1, 13.2, 13.3, 13.4_

- [x] 17. Implement home page and authentication pages
  - Create home page (frontend/src/pages/index.tsx) with hero section and call-to-action
  - Add sign-in and sign-up buttons using Clerk components
  - Create sign-in page (frontend/src/pages/sign-in/[[...index]].tsx) with Clerk SignIn component
  - Create sign-up page (frontend/src/pages/sign-up/[[...index]].tsx) with Clerk SignUp component
  - Style authentication pages with Tailwind CSS to match application design
  - Configure Clerk appearance prop for custom styling
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 14.1, 14.2, 14.3, 14.4_

- [x] 18. Implement navigation component
  - Create responsive navigation bar component
  - Add logo and navigation links (Home, Agent, Profile)
  - Integrate Clerk UserButton for authenticated users
  - Show sign-in/sign-up buttons for unauthenticated users
  - Implement mobile-responsive hamburger menu
  - Style with Tailwind CSS
  - _Requirements: 11.5, 14.1, 14.2, 14.3, 14.5_

- [x] 19. Implement profile page
  - Create profile page (frontend/src/pages/profile/[[...index]].tsx) as protected route
  - Add getServerSideProps for server-side authentication check
  - Integrate Clerk UserProfile component
  - Display user information from Clerk (name, email, profile picture)
  - Allow users to manage account settings, passwords, and connected accounts
  - Style page with Tailwind CSS
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 14.1, 14.2, 14.3_

- [x] 20. Implement agent interaction page layout
  - Create agent page (frontend/src/pages/agent.tsx) as protected route
  - Add getServerSideProps for server-side authentication check
  - Set up page layout with chat interface area and sidebar
  - Integrate useUser hook to get authenticated user information
  - Add loading states and error boundaries
  - Style page layout with Tailwind CSS
  - _Requirements: 12.1, 12.7, 14.1, 14.2, 14.3_
  - _Files: frontend/src/pages/agent.tsx_

- [x] 21. Implement ChatInterface component for agent page
  - Create ChatInterface component (frontend/src/components/ChatInterface.tsx) with message display
  - Add message input field and send button
  - Show user avatar from Clerk in messages
  - Display agent's task list for progress visibility (ready for backend integration)
  - Style with Tailwind CSS
  - _Requirements: 12.2, 12.4, 12.5, 12.7, 14.1, 14.2_
  - _Files: frontend/src/components/ChatInterface.tsx, frontend/src/pages/agent.tsx_

- [x] 22. Implement PropertyReviewPanel component for agent page
  - Create PropertyReviewPanel component (frontend/src/components/PropertyReviewPanel.tsx) triggered by interrupt
  - Display property cards with images, address, price, bedrooms, bathrooms
  - Add checkboxes for each property for approval/rejection
  - Implement submit button to resume agent with selections
  - Add loading state during resume
  - Style with Tailwind CSS
  - _Requirements: 12.3, 12.7, 14.1, 14.2_
  - _Files: frontend/src/components/PropertyReviewPanel.tsx, frontend/src/pages/agent.tsx_

- [x] 23. Implement PropertyReportView component for agent page
  - Create PropertyReportView component (frontend/src/components/PropertyReportView.tsx) for final report display
  - Display property details in card format with images
  - Display location analysis with nearby POIs and distances
  - Display pros and cons in structured lists
  - Add export or print functionality
  - Style with Tailwind CSS
  - _Requirements: 12.6, 12.7, 14.1, 14.2_
  - _Files: frontend/src/components/PropertyReportView.tsx, frontend/src/pages/agent.tsx_


- [x] 24. Implement frontend-backend integration for agent page
  - Use useAuth hook to get JWT token with getToken()
  - Create sendMessage function to call /api/invoke with Authorization header
  - Create resumeWithApprovals function to call /api/resume with Authorization header
  - Generate thread_id using user.id and timestamp
  - Handle interrupt detection and PropertyReviewPanel display
  - Add error handling and user feedback for API failures
  - Test complete workflow from authentication to property report
  - _Requirements: 12.3, 12.4, 12.7_
  - _Files: frontend/src/pages/agent.tsx_

- [ ]* 25. Write frontend component tests
  - Write tests for authentication flow with Clerk
  - Write tests for ChatInterface component
  - Write tests for PropertyReviewPanel component
  - Write tests for PropertyReportView component
  - _Requirements: 10, 11, 12, 14_

## Deployment

- [ ] 26. Prepare for deployment
  - Document local setup instructions in README
  - Create demo video showing application functionality
  - Ensure .kiro directory is committed to repository
  - Test complete workflow locally
  - Create deployment documentation for future production deployment
  - _Requirements: 8.1, 8.2, 13.5_

- [ ] 27. Set up monitoring
  - Configure LangSmith monitoring for agent
  - Set up error tracking
  - Monitor authentication events and user sessions
  - Create monitoring dashboard
