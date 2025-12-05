Induction App Project
Version History & Feature Summary
Development Log
December 5, 2025
Project Overview
The Induction Portal is a centralized, web-based onboarding tool designed to assist new employees
with IT setup procedures (VPN, MFA, Email). It features a user-friendly frontend for
employees and a password-protected Admin Panel for the IT team to manage content dynamically
without coding.
Key Capabilities (v19.0)
• Dynamic Content Management System (CMS): Add, edit, reorder, and delete categories
and steps directly from the browser.
• Multimedia Support: Handles images (PNG/JPG), video files (MP4/MOV), and external
links (YouTube, SharePoint).
• Deep Linking: Supports direct navigation to specific pages via URL parameters (e.g.,
/?page=vpn), enabling integration with browser extensions.
• Corporate Identity: Customizable Home Page with company logo and welcome message.
• Browser Extension: Companion extension for quick access to key modules.
1
Version History
Phase 1: Foundation (v1.0 – v5.0)
v1.0 - The Concept
• Initial prototype proposing the app structure.
• Hardcoded static text for basic tools (VPN, Outlook).
v2.0 - Streamlit Implementation
• Migration to Python Streamlit framework.
• Sidebar navigation menu implementation.
• Basic functions defined for MFA and VPN pages.
v3.0 - Asset Management
• Introduced file handling logic.
• Added support for loading local images from an images/ directory.
• Added support for downloadable PDF guides.
v4.0 - Admin Panel Beta
• New Feature: Password-protected Admin area (admin123).
• Basic file upload capability added to the sidebar.
v5.0 - Dynamic JSON Database
• Major Architecture Change: Moved from static code to a content_data.json database.
• Content (images + text) persists across sessions.
• Introduced "Edit & Reorder" functionality (Move Up/Down/Delete).
Phase 2: Enhanced UX & Features (v6.0 – v12.0)
v6.0 - Rich Text & Formatting
• Added Markdown support for text descriptions (Bold, Lists, Links).
• Added "Formatting Tips" helper in the Admin Panel.
• Introduced "Category Descriptions" (introductory text block before steps).
2
v7.0 - Home Page Customization
• Added a dedicated "Home Page Settings" tab in Admin.
• Admins can upload a Company Logo and edit the Welcome Message dynamically.
v8.0 - Software Center & UI Polish
• Added specific logic for the "Software Center" category.
• Implemented custom icon rendering for specific menu items.
• Deep Linking: Added URL parameter logic to support the browser extension integration.
v9.0 - Dynamic Categories
• Major Update: Categories are no longer hardcoded in Python.
• Added "Create New Category" tab in Admin Panel.
• Added "Delete Category" functionality ("Danger Zone").
• Implemented auto-migration to convert legacy hardcoded categories to JSON.
v10.0 - Video Support (Files)
• Admin Panel updated to accept video uploads (.mp4, .mov, .avi).
• Frontend updated to auto-detect file type and render a video player instead of an image.
v11.0 - Technical Debt Clean-up
• Fixed Streamlit deprecation warnings (use_container_width).
• Code refactoring for stability.
v12.0 - Video Support (URLs)
• Added "Add Video Link" input in Admin Panel.
• Support for YouTube and generic video URLs alongside file uploads.
Phase 3: Enterprise Integration (v13.0 – v19.0)
v13.0 - SharePoint Embed Experiment
• Attempted to use iframe components for SharePoint video links.
• Detected connectivity issues due to Microsoft security headers (X-Frame-Options).
v14.0 - Secure Link Fallback
• Smart Detection: App detects SharePoint/Microsoft Stream links.
• Replaced broken players with a secure "Watch on SharePoint" button (external link).
• Maintains standard player for YouTube/MP4.
3
v15.0 - Edit Mode Enhancements
• Added "Video URL" field to the Edit Content section (previously only available during
creation).
• Allowed retroactively adding links to existing steps.
v16.0 - Media Replacement
• Added "Replace Media (File Upload)" drag-and-drop zone in Edit Mode.
• Allows swapping an old image with a new video/image without deleting the step.
v17.0 - UI Simplification
• Cleaned up the "OR" logic in the UI.
• Both Upload and URL input methods are now displayed simultaneously for better usability.
v18.0 - Dual Media Logic
• Logic Update: Uploading a file no longer auto-clears the URL, and vice versa.
• Frontend updated to check for both media types.
v19.0 - Current Stable Version
• Feature: Simultaneous display of both Video Links (SharePoint/YouTube) AND Local
Files (Images/MP4) on the same step.
• Refined "Edit Content" interface to manage both media types independently.
• Full robust error handling for missing files.
4
