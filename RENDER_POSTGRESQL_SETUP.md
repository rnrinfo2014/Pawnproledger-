# Render PostgreSQL Setup Guide

## Step 1: Create PostgreSQL Database on Render

1. **Login to Render Dashboard**
   - Go to https://render.com
   - Sign in to your account

2. **Create New PostgreSQL Database**
   - Click "New +" button
   - Select "PostgreSQL"
   - Fill in the details:
     - **Name**: `pawnpro-db` (or your preferred name)
     - **Database**: `pawnpro_db`
     - **User**: `pawnpro_user`
     - **Region**: Choose closest to your location
     - **PostgreSQL Version**: 15 (recommended)
     - **Plan**: Free tier or paid based on your needs

3. **Get Connection Details**
   After creation, you'll get connection details like:
   ```
   Host: dpg-xxxxx-pool.oregon-postgres.render.com
   Port: 5432
   Database: pawnpro_db
   Username: pawnpro_user
   Password: [generated password]
   ```

## Step 2: Configure Your Application

### Option A: Using Environment Variable (Recommended for Production)

1. **Set DATABASE_URL environment variable**
   ```bash
   # Format: postgresql://username:password@hostname:port/database_name
   export DATABASE_URL="postgresql://pawnpro_user:your_password@dpg-xxxxx-pool.oregon-postgres.render.com/pawnpro_db"
   ```

2. **For Render Web Service deployment**
   - In Render dashboard, go to your web service
   - Go to "Environment" tab
   - Add environment variable:
     - **Key**: `DATABASE_URL`
     - **Value**: `postgresql://pawnpro_user:your_password@dpg-xxxxx-pool.oregon-postgres.render.com/pawnpro_db`

### Option B: Using .env File (Local Development)

1. **Create .env file in PawnProApi directory**
   ```bash
   cp .env.example .env
   ```

2. **Edit .env file**
   ```
   ENVIRONMENT=production
   DATABASE_URL=postgresql://pawnpro_user:your_password@dpg-xxxxx-pool.oregon-postgres.render.com/pawnpro_db
   SECRET_KEY=your-super-secret-jwt-key-here
   ```

## Step 3: Test Database Connection

1. **Run the connection test script**
   ```bash
   cd PawnProApi
   python test_db_connection.py
   ```

2. **Expected output for successful connection**
   ```
   ==================================================
   PawnSoft Database Connection Test
   ==================================================
   Testing database connection...
   Environment: production
   Database URL: postgresql://pawnpro_user:****@dpg-xxxxx-pool.oregon-postgres.render.com/pawnpro_db
   Using SSL connection for production/Render database
   ✅ Database connection successful!
   PostgreSQL version: PostgreSQL 15.x on x86_64-pc-linux-gnu
   ✅ Test query successful: 1
   ==================================================
   ✅ All tests passed! Database is ready.
   ```

## Step 4: Initialize Database Tables

1. **Run table creation script**
   ```bash
   python create_tables.py
   ```

2. **Verify tables are created**
   - Check Render dashboard database console
   - Or run a test API call to verify

## Step 5: Deploy to Render (Optional)

If you want to deploy your API to Render:

1. **Create Web Service on Render**
   - Connect your GitHub repository
   - Set build command: `cd PawnProApi && pip install -r requirements.txt`
   - Set start command: `cd PawnProApi && uvicorn main:app --host 0.0.0.0 --port $PORT`

2. **Environment Variables for Web Service**
   ```
   DATABASE_URL=postgresql://pawnpro_user:your_password@dpg-xxxxx-pool.oregon-postgres.render.com/pawnpro_db
   ENVIRONMENT=production
   SECRET_KEY=your-super-secret-jwt-key-here
   ```

## Troubleshooting

### Connection Issues
- **SSL Error**: Make sure SSL is enabled in production (handled automatically in our config)
- **Host/Port Error**: Double-check the connection string from Render dashboard
- **Authentication Error**: Verify username and password are correct

### Database Issues
- **Tables not found**: Run `python create_tables.py` to initialize
- **Permission Error**: Check if user has proper permissions on the database

### Application Issues
- **Import Error**: Make sure all dependencies are installed: `pip install -r requirements.txt`
- **Environment Error**: Verify environment variables are set correctly

## Security Notes

1. **Never commit .env file**: It's already in .gitignore
2. **Use strong SECRET_KEY**: Generate a secure random string
3. **Rotate passwords**: Consider rotating database passwords periodically
4. **Use environment variables**: Don't hardcode credentials in code

## Connection String Formats

### Internal Database URL (for Render services)
```
postgresql://pawnpro_user:password@dpg-xxxxx/pawnpro_db
```

### External Database URL (for external connections)
```
postgresql://pawnpro_user:password@dpg-xxxxx-pool.oregon-postgres.render.com/pawnpro_db
```

Use the **External URL** for connecting from your local development environment or external services.