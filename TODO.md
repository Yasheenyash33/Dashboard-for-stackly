# TODO: Role-Based User Management and Reporting System

## Backend Changes
- [ ] Update models.py: Add is_temporary_password field to User model
- [ ] Update schemas.py: Add is_temporary to UserCreate, UserUpdate, User schemas; update TokenResponse with force_password_change
- [ ] Update crud.py: Modify create_user to handle is_temporary_password
- [ ] Update main.py: Modify login endpoint to check and return force_password_change; add /reports/generate endpoint for PDF/Excel/CSV downloads
- [ ] Update requirements.txt: Add reportlab, openpyxl, pandas for report generation

## Frontend Changes
- [ ] Update AuthContext.jsx: Handle force_password_change in login response and redirect to change password
- [ ] Update ChangePassword.jsx: Use updateUserById to update password and set is_temporary to false
- [ ] Update Analytics.jsx: Replace JSON export with backend report generation for PDF/Excel/CSV
- [ ] Update App.jsx: Add route for /change-password

## Testing and Deployment
- [ ] Install backend dependencies
- [ ] Test user creation with temporary password
- [ ] Test login with force password change
- [ ] Test report generation and download
- [ ] Verify real-time updates via WebSocket
