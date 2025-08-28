# News Site - Blog Platform with Subscription System

A modern web platform for blogging with monetization through subscriptions. The project is built on Django REST API (backend) and Vue.js (frontend) with Stripe integration for payments.

## 🚀 Key Features

### For Users

- **Registration and Authentication** - JWT tokens, token refresh
- **Profile Management** - data editing, password change
- **Post Creation and Management** - WYSIWYG editor, image uploads
- **Comment System** - multi-level comments with replies
- **Post Categorization** - content organization by topics
- **Search and Filtering** - quick search across posts and comments

### Premium Features (Subscription)

- **Post Pinning** - highlighting important content at the top
- **Priority Display** - pinned posts appear first
- **Statistics** - detailed analytics for authors

### Administrative Features

- **Content Moderation** - managing posts and comments
- **Payment Analytics** - reports on revenue and subscriptions
- **User Management** - access rights and roles
- **Webhook Processing** - automatic synchronization with Stripe

## 🛠 Technology Stack

### Backend

- **Django 5.2** - main web framework
- **Django REST Framework** - API interfaces
- **PostgreSQL** - main database
- **Redis** - caching and task queues
- **Celery** - asynchronous tasks
- **Stripe API** - payment system

### Frontend

- **Vue.js 3** - modern frontend framework
- **Pinia** - state management
- **Vue Router** - routing
- **Tailwind CSS** - styling
- **Axios** - HTTP client

### DevOps

- **Docker & Docker Compose** - containerization
- **Nginx** - reverse proxy and static files
- **Let's Encrypt** - SSL certificates
- **Gunicorn** - WSGI server

## 📋 Project Structure

```
news-site/
├── backend/                 # Django application
│   ├── apps/
│   │   ├── accounts/       # Users and authentication
│   │   ├── main/           # Posts and categories
│   │   ├── comments/       # Comment system
│   │   ├── subscribe/      # Subscriptions and premium features
│   │   └── payment/        # Payment system
│   ├── config/             # Django settings
│   └── manage.py
├── frontend/               # Vue.js application
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── views/          # Application pages
│   │   ├── stores/         # Pinia stores
│   │   ├── router/         # Routing
│   │   └── services/       # API clients
│   └── package.json
├── docker-compose.yml      # Container orchestration
├── nginx.conf             # Web server configuration
└── .env                   # Environment variables
```

## 🎯 Core Data Models

### User

- Extended Django user model
- Avatar and biography support
- JWT authentication

### Post

- Title, content, images
- Status system (draft/published)
- View and comment counters
- SEO-friendly URL (slug)

### Comment

- Multi-level reply system
- Soft delete functionality
- Moderation and management

### Subscription

- Pricing plans with different features
- Automatic renewal
- Stripe integration

### Payment

- Complete transaction history
- Stripe webhook processing
- Refund system

## 🔧 API Endpoints

### Authentication

```
POST /api/v1/auth/register/      # Registration
POST /api/v1/auth/login/         # Login
POST /api/v1/auth/logout/        # Logout
GET  /api/v1/auth/profile/       # User profile
PUT  /api/v1/auth/profile/       # Profile update
POST /api/v1/auth/token/refresh/ # Token refresh
```

### Posts and Categories

```
GET  /api/v1/posts/              # Post list
POST /api/v1/posts/              # Create post
GET  /api/v1/posts/{slug}/       # Post details
PUT  /api/v1/posts/{slug}/       # Update post
GET  /api/v1/posts/popular/      # Popular posts
GET  /api/v1/posts/categories/   # Categories
```

### Comments

```
GET  /api/v1/comments/           # All comments
POST /api/v1/comments/           # Create comment
GET  /api/v1/comments/post/{id}/ # Post comments
GET  /api/v1/comments/{id}/replies/ # Comment replies
```

### Subscriptions and Payments

```
GET  /api/v1/subscribe/plans/    # Pricing plans
GET  /api/v1/subscribe/status/   # Subscription status
POST /api/v1/subscribe/pin-post/ # Pin post
POST /api/v1/payment/create-checkout-session/ # Create checkout session
```

## 🌟 Architecture Features

### Pinned Posts System

- Only subscribers can pin posts
- Automatic subscription activity check
- Smart sorting in news feed

### Payment Integration

- Stripe Checkout for secure payments
- Webhook processing for status synchronization
- Retry system for failed payments

### Performance

- Caching of frequently requested data
- Pagination for all lists
- Optimized SQL queries with select_related

### Security

- JWT tokens with auto-refresh
- CORS settings for cross-domain requests
- Rate limiting for API endpoints
- User input validation and sanitization

## 💾 Database

The project uses PostgreSQL with the following main tables:

- `users` - users
- `posts` - blog posts
- `categories` - post categories
- `comments` - comments
- `subscriptions` - user subscriptions
- `subscription_plans` - pricing plans
- `payments` - payments
- `pinned_posts` - pinned posts

## 🔄 Asynchronous Tasks (Celery)

- **Check expired subscriptions** - hourly
- **Send renewal reminders** - daily
- **Clean old payments** - weekly
- **Process webhook events** - on demand
- **Generate reports** - scheduled

## 🚀 Deployment

### Requirements

- Docker and Docker Compose
- Domain with SSL certificate
- Stripe account for payments

### Quick Start

1. Clone repository
2. Create `.env` file based on `.env.example`
3. Configure Stripe keys and webhook endpoints
4. Run with `docker-compose up -d`
5. System will automatically apply migrations and collect static files

### Nginx Configuration

- Automatic HTTP → HTTPS redirect
- Static file compression
- Image and media caching
- API rate limiting
- Proxying to Django and Vue.js services

## 📊 Monitoring and Logging

- Nginx access and error logs
- Django logging for all operations
- Celery logs for asynchronous tasks
- Stripe webhook logs for payment debugging

## 🧪 Testing

The project includes API testing via Postman:

- Complete collection for testing all endpoints
- Automatic token management
- Response and data structure validation
- Edge cases and error testing

## 📝 License

The project was developed to demonstrate the capabilities of modern web development using Django and Vue.js. Includes best practices for security, performance, and scalability.