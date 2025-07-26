# Release Notes

## v0.0.1 - Initial Release (2024-07-26)

### 🎉 First stable release of Remnawave Telegram Bot

**Полнофункциональный Telegram бот для управления промо-кампаниями через панель Remnawave**

### ✨ Features

#### 🎁 Promo Campaign Management
- ✅ **Create promo campaigns** with tag validation (latin only, snake_case)
- ✅ **Traffic limit selection** via inline buttons (15GB, 30GB, 50GB, 100GB)
- ✅ **Bulk subscription creation** (1-100 subscriptions)
- ✅ **Automatic username generation** (`promo-{random}-{tag}` format)
- ✅ **Unlimited time** subscriptions with traffic limits only
- ✅ **TXT file generation** with subscription links
- ✅ **Detailed creation reports**

#### 🗑 Subscription Management
- ✅ **List existing tags** with usage statistics
- ✅ **Preview statistics** before deletion (total/active/used)
- ✅ **Delete only used subscriptions** with confirmation
- ✅ **Detailed deletion reports**

#### 📊 Statistics & Monitoring
- ✅ **Global campaign statistics**
- ✅ **Per-tag detailed breakdown**
- ✅ **Real-time usage tracking**
- ✅ **Active vs used subscription counts**

#### 🎨 Modern UI/UX
- ✅ **Inline keyboards everywhere** - no text commands
- ✅ **Message editing** instead of sending new messages
- ✅ **Auto-delete user messages** for clean interface
- ✅ **"Back to main menu"** buttons in all appropriate places
- ✅ **Input validation** with helpful error messages
- ✅ **Progress indicators** for long operations

#### 🐳 Docker Integration
- ✅ **Multi-environment support** (development & production)
- ✅ **Optimized Dockerfile** with Python 3.11-slim
- ✅ **Resource limits** and health checks
- ✅ **Auto-restart policies** for reliability
- ✅ **Watchtower integration** for automatic updates (prod)
- ✅ **Helper scripts** for easy management
- ✅ **Security hardening** with non-root user

#### 🛡 Security & Reliability
- ✅ **Admin authentication** via ADMIN_USER_IDS
- ✅ **Full input validation** and sanitization
- ✅ **Comprehensive error handling** for all API calls
- ✅ **Detailed logging** with configurable levels
- ✅ **Environment variable configuration**
- ✅ **Graceful degradation** on API failures

### 🚀 Deployment Options

1. **🐳 Docker (Recommended)**
   ```bash
   ./docker-scripts/start.sh --prod
   ```

2. **📦 Manual Installation**
   ```bash
   pip install -r requirements.txt
   python main.py
   ```

3. **🔧 Systemd Service**
   - Auto-start on boot
   - Service management

### 📚 Documentation

- ✅ **README.md** - comprehensive overview
- ✅ **INSTALL.md** - detailed installation guide
- ✅ **DOCKER.md** - complete Docker documentation
- ✅ **QUICK_START.md** - 5-minute setup guide
- ✅ **PROJECT_STRUCTURE.md** - architecture documentation
- ✅ **Inline code documentation** with docstrings

### 🧪 Testing

- ✅ **Configuration validation** tests
- ✅ **Import and dependency** tests
- ✅ **Input validation** tests
- ✅ **Docker configuration** tests
- ✅ **File management** tests

### 📦 Package Dependencies

```
remnawave-api==1.1.3      # Remnawave SDK integration
python-telegram-bot==22.3  # Modern Telegram Bot API
python-dotenv==1.0.0       # Environment configuration
aiofiles==24.1.0           # Async file operations
PyYAML==6.0.2              # YAML parsing for tests
```

### 🔧 Configuration

**Required Environment Variables:**
- `TELEGRAM_BOT_TOKEN` - Bot token from @BotFather
- `REMNAWAVE_BASE_URL` - Remnawave panel URL
- `REMNAWAVE_TOKEN` - API token for Remnawave
- `ADMIN_USER_IDS` - Authorized user IDs

**Optional Configuration:**
- `REMNAWAVE_CADDY_TOKEN` - Caddy auth token
- `DEFAULT_INBOUND_IDS` - Inbound IDs for user creation
- `MAX_SUBSCRIPTIONS_PER_REQUEST` - Subscription limits
- `LOG_LEVEL` - Logging verbosity

### 🏗 Architecture

**Modular Design:**
- `main.py` - Application entry point
- `config.py` - Configuration management
- `bot_handlers.py` - Telegram command handlers
- `remnawave_service.py` - Remnawave API integration
- `utils.py` - Helper functions and utilities

**Async/Await Pattern:**
- Non-blocking I/O operations
- Concurrent request handling
- Efficient resource utilization

### 🔄 Management Commands

```bash
# Docker management
./docker-scripts/start.sh [--prod]    # Start containers
./docker-scripts/stop.sh [--prod]     # Stop containers

# Monitoring
docker logs promo-remna-bot -f # View logs
docker stats promo-remna-bot   # Resource usage

# Testing
python3 test_bot.py        # Application tests
python3 test_docker.py     # Docker configuration tests
```

### 📊 Performance

**Resource Usage:**
- **Development:** 512MB RAM, 0.5 CPU cores
- **Production:** 1GB RAM, 1.0 CPU cores
- **Storage:** Minimal (logs and subscription files)

**Scalability:**
- Handles 1-100 subscriptions per request
- Configurable rate limits
- Efficient API usage patterns

### 🎯 Production Ready

**Reliability Features:**
- Health checks every 30-60 seconds
- Automatic restart on failures
- Comprehensive error logging
- Graceful shutdown handling

**Security Features:**
- No elevated privileges required
- Isolated container networking
- Environment-based secrets
- Input sanitization and validation

### 🐞 Known Issues

- None reported in this initial release

### 🔮 Future Roadmap

- [ ] Web dashboard for campaign management
- [ ] Webhook support for real-time updates
- [ ] Advanced analytics and reporting
- [ ] Multi-language support
- [ ] Backup/restore functionality

### 👥 Contributors

- Initial development and architecture
- Docker integration and optimization
- Comprehensive documentation
- Testing framework implementation

### 🔄 Repository Updates

**Main Branch Migration:**
- ✅ **Stable Main Branch** - All releases now published on main branch
- ✅ **Updated URLs** - All documentation uses correct GitHub repository URLs
- ✅ **Container Naming** - Simplified to `promo-remna-bot` and `promo-remna-bot-prod`
- ✅ **Installation Paths** - Updated to use `PromoRemnaBot` directory name
- ✅ **Service Files** - SystemD and Docker configs reflect new structure

**Breaking Changes:**
- Container names changed from `remnawave-telegram-bot` to `promo-remna-bot`
- Repository clone path changed to `PromoRemnaBot` directory
- Main branch is now the primary development and release branch

### 📄 License

This project is licensed under the **MIT License** - see the LICENSE file for details.

**MIT License Benefits:**
- ✅ **Commercial Use Allowed** - Use in commercial projects without restrictions
- ✅ **Modification Allowed** - Freely modify and distribute modified versions
- ✅ **Distribution Allowed** - Share the software with anyone
- ✅ **Private Use Allowed** - Use privately without obligation to share
- ✅ **No Copyleft** - No requirement to open source derivative works
- ✅ **Minimal Requirements** - Only copyright notice and license text required

---

**Download:** https://github.com/graf4ik322/PromoRemnaBot/releases/tag/v0.0.1

**Repository:** https://github.com/graf4ik322/PromoRemnaBot

**Quick Start:** `git clone https://github.com/graf4ik322/PromoRemnaBot.git && cd PromoRemnaBot && ./docker-scripts/start.sh --prod`