# Implementation Plan

## Backend: LangGraph/Deep Agent Implementation

- [x] 1. Set up project structure and dependencies
  - Initialize Python project with uv (uv init)
  - Create pyproject.toml with project metadata
  - Install deepagents, langgraph, langchain packages with uv add
  - Install FastAPI and fastapi-clerk-auth packages with uv add
  - Install Tavily and Mapbox SDK packages with uv add
  - Install psycopg2-binary for PostgreSQL checkpointer with uv add
  - Create requirements.txt from uv dependencies
  - Create .env file from .env.example for API keys
  - Create directory structure: api/ (index.py), src/ (agent.py, tools.py, models.py, utils.py), pages/, tests/
  - Run uv sync to create virtual environment and install dependencies
  - _Requirements: All requirements depend on proper setup_

- [x] 2. Implement core data models
  - Create Property model with all required fields (id, address, price, bedrooms, bathrooms, etc.)
  - Create SearchCriteria model with location, price range, and property type filters
  - Create PointOfInterest model for location data
  - Create LocationAnalysis model with POIs, pros, cons, and scores
  - Create PropertyReport model to structure final output
  - _Requirements: 2.1, 4.1, 5.1_

- [x] 3. Implement Tavily search tool
  - Create tavily_search_tool function that accepts query, max_results, and search_depth parameters
  - Implement property data extraction from Tavily search results
  - Implement image URL extraction from search results
  - Add error handling for API failures
  - _Requirements: 2.2, 2.3, 2.4_

- [ ] 4. Implement Mapbox location tools
  - Create mapbox_geocode_tool to convert addresses to coordinates
  - Create mapbox_nearby_tool to find POIs by category and radius
  - Implement distance calculation utility function
  - Add error handling for geocoding failures
  - _Requirements: 4.2, 4.3, 4.4_

- [ ] 5. Implement rate limit handling
  - Create RateLimitHandler class with exponential backoff logic
  - Wrap Tavily API calls with retry logic
  - Wrap Mapbox API calls with retry logic
  - Add logging for rate limit events
  - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [ ] 6. Implement Property Search Sub-Agent
  - Define property_search_agent configuration with name, description, and system prompt
  - Write system prompt instructing agent to use Tavily tool and write results to filesystem
  - Configure agent with tavily_search_tool
  - Implement logic to write each property to separate JSON file in /properties/ directory
  - Implement summary generation of found properties
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 6.2_

- [ ] 7. Implement Location Analysis Sub-Agent
  - Define location_analysis_agent configuration with name, description, and system prompt
  - Write system prompt instructing agent to use Mapbox tools and analyze locations
  - Configure agent with mapbox_geocode_tool and mapbox_nearby_tool
  - Implement logic to search for POIs in categories: shopping, schools, transit, parks, workplaces
  - Implement pros/cons analysis logic based on nearby amenities
  - Implement logic to write analysis to /locations/ directory
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

- [ ] 8. Implement Supervisor Agent
  - Create supervisor agent using create_deep_agent with Claude model
  - Write comprehensive system prompt for conversation management and coordination
  - Configure agent with property_search_agent and location_analysis_agent as subagents
  - Implement search criteria extraction from natural language
  - Configure checkpointer (MemorySaver for dev)
  - Define SupervisorState schema with messages, todos, search_criteria, approved_properties, filesystem
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 7.1, 8.1, 8.2, 8.3_

- [ ] 9. Implement human-in-the-loop interrupt
  - Configure interrupt_on parameter for supervisor agent with "present_properties_for_review" trigger
  - Implement logic to trigger interrupt after Property Search Agent completes
  - Implement interrupt payload with property summaries and images
  - Implement resume logic to accept approved_properties input
  - Implement re-search logic when properties are rejected
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [ ] 10. Implement report compilation
  - Implement logic to read property files from /properties/ directory
  - Implement logic to read location analysis files from /locations/ directory
  - Implement PropertyReport generation combining all data
  - Format report with property details, images, location analysis, pros/cons
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 11. Write integration tests for LangGraph workflow
  - Write test for complete property search workflow with invoke
  - Write test for human-in-the-loop interrupt and resume
  - Write test for property rejection and re-search flow
  - Write test for error handling with invalid location
  - _Requirements: All requirements_

- [ ]* 12. Write unit tests for core utilities
  - Write test for search criteria extraction logic
  - Write test for distance calculation utility
  - Write test for rate limit retry logic
  - _Requirements: 1.2, 4.4, 9.1_

- [ ]* 13. Write trajectory tests with AgentEvals
  - Write trajectory match test for expected tool call sequence
  - Write LLM-as-judge test for agent decision quality
  - _Requirements: All requirements_

- [ ] 14. Implement FastAPI server (api/index.py)
  - Create api/index.py with FastAPI app
  - Set up ClerkConfig with CLERK_JWKS_URL from environment
  - Create ClerkHTTPBearer guard for authentication
  - Implement POST /api/invoke endpoint with Clerk auth
  - Implement POST /api/resume endpoint with Clerk auth
  - Implement GET /api/state endpoint with Clerk auth
  - Import supervisor_agent from src/agent.py
  - Extract user_id from creds.decoded["sub"] for thread isolation
  - Test API endpoints locally with JWT token
  - _Requirements: 8.1, 8.2, 12.3, 12.4, 13.1, 13.2_

- [ ] 15. Set up LangSmith monitoring for backend
  - Configure LangSmith API key in environment variables
  - Add tracing to supervisor agent
  - Set up error logging and alerting
  - Create dashboard for monitoring agent performance
  - _Requirements: 9.5_

## Frontend: Next.js with Clerk Authentication

- [ ] 16. Create Next.js frontend project with Clerk authentication
  - Initialize Next.js 14+ project with TypeScript and Pages Router
  - Install @clerk/nextjs package for authentication
  - Install and configure Tailwind CSS
  - Set up project structure with /pages, /components, /lib, /styles directories
  - Configure environment variables: NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY, CLERK_SECRET_KEY, CLERK_JWKS_URL
  - Note: API calls go to /api (same domain, no separate API_URL needed)
  - _Requirements: 10.1, 10.2, 10.3, 13.5, 14.1_

- [ ] 17. Set up Clerk authentication and route protection
  - Wrap application with ClerkProvider in pages/_app.tsx
  - Create middleware.ts with clerkMiddleware for route protection
  - Define protected routes: /agent and /profile
  - Add getServerSideProps to protected pages for server-side auth checks
  - Configure redirect URLs for sign-in and sign-up flows
  - Test authentication flow and route protection
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 13.1, 13.2, 13.3, 13.4_

- [ ] 18. Implement home page and authentication pages
  - Create home page (pages/index.tsx) with hero section and call-to-action
  - Add sign-in and sign-up buttons using Clerk components
  - Create sign-in page (pages/sign-in/[[...index]].tsx) with Clerk SignIn component
  - Create sign-up page (pages/sign-up/[[...index]].tsx) with Clerk SignUp component
  - Style authentication pages with Tailwind CSS to match application design
  - Configure Clerk appearance prop for custom styling
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 14.1, 14.2, 14.3, 14.4_

- [ ] 19. Implement navigation component
  - Create responsive navigation bar component
  - Add logo and navigation links (Home, Agent, Profile)
  - Integrate Clerk UserButton for authenticated users
  - Show sign-in/sign-up buttons for unauthenticated users
  - Implement mobile-responsive hamburger menu
  - Style with Tailwind CSS
  - _Requirements: 11.5, 14.1, 14.2, 14.3, 14.5_

- [ ] 20. Implement profile page
  - Create profile page (pages/profile/[[...index]].tsx) as protected route
  - Add getServerSideProps for server-side authentication check
  - Integrate Clerk UserProfile component
  - Display user information from Clerk (name, email, profile picture)
  - Allow users to manage account settings, passwords, and connected accounts
  - Style page with Tailwind CSS
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 14.1, 14.2, 14.3_

- [ ] 21. Implement agent interaction page layout
  - Create agent page (pages/agent.tsx) as protected route
  - Add getServerSideProps for server-side authentication check
  - Set up page layout with chat interface area and sidebar
  - Integrate useUser hook to get authenticated user information
  - Configure useStream hook with user-specific thread_id
  - Add loading states and error boundaries
  - Style page layout with Tailwind CSS
  - _Requirements: 12.1, 12.7, 14.1, 14.2, 14.3_

- [ ] 22. Implement ChatInterface component for agent page
  - Create ChatInterface component with message display
  - Implement useStream hook integration for streaming responses
  - Display agent's task list for progress visibility
  - Add message input field and send button
  - Show user avatar from Clerk in messages
  - Style with Tailwind CSS
  - _Requirements: 12.2, 12.4, 12.5, 12.7, 14.1, 14.2_

- [ ] 23. Implement PropertyReviewPanel component for agent page
  - Create PropertyReviewPanel component triggered by interrupt
  - Display property cards with images, address, price, bedrooms, bathrooms
  - Add checkboxes for each property for approval/rejection
  - Implement submit button to resume agent with selections
  - Add loading state during resume
  - Style with Tailwind CSS
  - _Requirements: 12.3, 12.7, 14.1, 14.2_

- [ ] 24. Implement PropertyReportView component for agent page
  - Create PropertyReportView component for final report display
  - Display property details in card format with images
  - Display location analysis with nearby POIs and distances
  - Display pros and cons in structured lists
  - Add export or print functionality
  - Style with Tailwind CSS
  - _Requirements: 12.6, 12.7, 14.1, 14.2_

- [ ] 25. Implement frontend-backend integration for agent page
  - Use useAuth hook to get JWT token with getToken()
  - Create sendMessage function to call /api/invoke with Authorization header
  - Create resumeWithApprovals function to call /api/resume with Authorization header
  - Generate thread_id using user.id and timestamp
  - Handle interrupt detection and PropertyReviewPanel display
  - Add error handling and user feedback for API failures
  - Test complete workflow from authentication to property report
  - _Requirements: 12.3, 12.4, 12.7_

- [ ]* 26. Write frontend component tests
  - Write tests for authentication flow with Clerk
  - Write tests for ChatInterface component
  - Write tests for PropertyReviewPanel component
  - Write tests for PropertyReportView component
  - _Requirements: 10, 11, 12, 14_

## Deployment

- [ ] 27. Deploy to Vercel
  - Create vercel.json configuration file
  - Create requirements.txt for Python dependencies
  - Set up Vercel Postgres database
  - Configure environment variables: NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY, CLERK_SECRET_KEY, CLERK_JWKS_URL, ANTHROPIC_API_KEY, TAVILY_API_KEY, MAPBOX_API_KEY, DATABASE_URL, LANGSMITH_API_KEY
  - Configure Clerk production instance and get JWKS URL
  - Deploy to Vercel (frontend pages + api/index.py serverless function)
  - Test end-to-end workflow in production
  - Create deployment documentation
  - _Requirements: 8.1, 8.2, 13.5_

- [ ] 28. Set up production monitoring
  - Configure LangSmith monitoring for production agent
  - Set up Vercel Analytics for frontend performance
  - Monitor Vercel function logs
  - Monitor authentication events and user sessions
  - Create monitoring dashboard
  - _Requirements: 9.5_
