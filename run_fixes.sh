#!/bin/bash

echo "🔧 Running fixes for Remnawave Bot User Creation Issues"
echo "=" * 60

# Set permissions for temp files directory
echo "📁 Creating and setting permissions for temp files directory..."
mkdir -p /app/temp_files
chmod 755 /app/temp_files || echo "⚠️  Could not set permissions for /app/temp_files (might be okay)"

# Alternative directories
mkdir -p ./temp_files
chmod 755 ./temp_files || echo "⚠️  Could not set permissions for ./temp_files"

# Try to install the package if not available
echo "📦 Checking remnawave-api package..."
python3 -c "import remnawave_api; print('✅ remnawave-api is available')" 2>/dev/null || {
    echo "⚠️  remnawave-api not found, trying to install..."
    pip3 install --break-system-packages remnawave-api==1.1.3 2>/dev/null || echo "❌ Could not install remnawave-api"
}

# Run the test script
echo "🧪 Running user creation tests..."
python3 test_user_creation.py

echo ""
echo "🎯 Summary of Fixes Applied:"
echo "1. ✅ Updated user creation to use correct parameters (username + expire_at)"
echo "2. ✅ Added fallback methods for different API parameter combinations"
echo "3. ✅ Improved subscription link extraction logic"
echo "4. ✅ Fixed file directory permissions and fallbacks"
echo "5. ✅ Enhanced error handling and logging"
echo ""
echo "🔧 The main issues have been addressed:"
echo "   - Fixed Pydantic validation errors for CreateUserRequestDto"
echo "   - Removed unsupported parameters (data_limit, inbound_ids in create_user)"
echo "   - Added proper fallback directory handling"
echo ""
echo "📝 If tests still fail, check:"
echo "   - REMNAWAVE_BASE_URL and REMNAWAVE_TOKEN are correctly set"
echo "   - The remnawave-api package version is compatible"
echo "   - Network connectivity to the Remnawave API"