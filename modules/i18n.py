"""
Internationalization (i18n) Module for the Induction App
Provides multi-language support (EN/RO/IT)
"""
import streamlit as st

# UI Translations
TRANSLATIONS = {
    "en": {
        # Navigation
        "home": "🏠 Home",
        "faq": "❓ FAQ / Help",
        "admin": "⚙️ Admin Panel",
        "search_placeholder": "🔍 Search guide...",
        "my_bookmarks": "⭐ My Bookmarks",
        
        # Guide Page
        "progress": "📊 Progress",
        "steps": "steps",
        "of": "of",
        "mark_done": "⭕ Mark as Done",
        "completed": "✅ Completed",
        "print_guide": "🖨️ Print Guide",
        "direct_link": "🔗 Direct Link",
        "bookmark": "☆ Bookmark",
        "bookmarked": "⭐ Bookmarked",
        "time_estimate": "⏱️ ~{} minutes",
        
        # Feedback
        "helpful": "👍 Yes",
        "not_helpful": "👎 No",
        "was_helpful": "Was this guide helpful?",
        "thanks_feedback": "Thanks for your feedback!",
        "will_improve": "We'll try to improve.",
        
        # Celebration
        "congratulations": "🎉 Congratulations!",
        "completed_all": "You have completed all {} steps in this guide!",
        
        # Home Page
        "quick_start": "🚀 Quick Start",
        "quick_start_desc": "Jump straight to the most useful guides:",
        "setup_mfa": "🔐 Setup MFA",
        "connect_vpn": "🛡️ Connect VPN",
        "email_setup": "📧 Email Setup",
        "select_guide": "👈 Please select a guide from the sidebar to get started.",
        
        # Misc
        "need_help": "💬 Need Help?",
        "extension_title": "🧩 Browser Extension",
        "extension_desc": "Quick access to guides directly from your toolbar.",
        "download_extension": "📥 Download Extension",
        "never": "Never",
        "views": "views",
        "completions": "completions"
    },
    "ro": {
        # Navigation
        "home": "🏠 Acasă",
        "faq": "❓ FAQ / Ajutor",
        "admin": "⚙️ Panou Admin",
        "search_placeholder": "🔍 Caută ghid...",
        "my_bookmarks": "⭐ Bookmark-urile Mele",
        
        # Guide Page
        "progress": "📊 Progres",
        "steps": "pași",
        "of": "din",
        "mark_done": "⭕ Marchează ca făcut",
        "completed": "✅ Completat",
        "print_guide": "🖨️ Printează Ghid",
        "direct_link": "🔗 Link Direct",
        "bookmark": "☆ Bookmark",
        "bookmarked": "⭐ Salvat",
        "time_estimate": "⏱️ ~{} minute",
        
        # Feedback
        "helpful": "👍 Da",
        "not_helpful": "👎 Nu",
        "was_helpful": "A fost de ajutor acest ghid?",
        "thanks_feedback": "Mulțumim pentru feedback!",
        "will_improve": "Vom încerca să îmbunătățim.",
        
        # Celebration
        "congratulations": "🎉 Felicitări!",
        "completed_all": "Ai completat toți {} pașii din acest ghid!",
        
        # Home Page
        "quick_start": "🚀 Start Rapid",
        "quick_start_desc": "Sari direct la cele mai utile ghiduri:",
        "setup_mfa": "🔐 Configurare MFA",
        "connect_vpn": "🛡️ Conectare VPN",
        "email_setup": "📧 Configurare Email",
        "select_guide": "👈 Selectează un ghid din stânga pentru a începe.",
        
        # Misc
        "need_help": "💬 Ai nevoie de ajutor?",
        "extension_title": "🧩 Extensie Browser",
        "extension_desc": "Acces rapid la ghiduri direct din bara de instrumente.",
        "download_extension": "📥 Descarcă Extensia",
        "never": "Niciodată",
        "views": "vizualizări",
        "completions": "completări"
    },
    "it": {
        # Navigation
        "home": "🏠 Home",
        "faq": "❓ FAQ / Aiuto",
        "admin": "⚙️ Pannello Admin",
        "search_placeholder": "🔍 Cerca guida...",
        "my_bookmarks": "⭐ I Miei Segnalibri",
        
        # Guide Page
        "progress": "📊 Progresso",
        "steps": "passi",
        "of": "di",
        "mark_done": "⭕ Segna come fatto",
        "completed": "✅ Completato",
        "print_guide": "🖨️ Stampa Guida",
        "direct_link": "🔗 Link Diretto",
        "bookmark": "☆ Segnalibro",
        "bookmarked": "⭐ Salvato",
        "time_estimate": "⏱️ ~{} minuti",
        
        # Feedback
        "helpful": "👍 Sì",
        "not_helpful": "👎 No",
        "was_helpful": "Questa guida è stata utile?",
        "thanks_feedback": "Grazie per il feedback!",
        "will_improve": "Cercheremo di migliorare.",
        
        # Celebration
        "congratulations": "🎉 Congratulazioni!",
        "completed_all": "Hai completato tutti i {} passi di questa guida!",
        
        # Home Page
        "quick_start": "🚀 Avvio Rapido",
        "quick_start_desc": "Vai direttamente alle guide più utili:",
        "setup_mfa": "🔐 Configura MFA",
        "connect_vpn": "🛡️ Connetti VPN",
        "email_setup": "📧 Configurazione Email",
        "select_guide": "👈 Seleziona una guida dalla barra laterale per iniziare.",
        
        # Misc
        "need_help": "💬 Hai bisogno di aiuto?",
        "extension_title": "🧩 Estensione Browser",
        "extension_desc": "Accesso rapido alle guide direttamente dalla barra degli strumenti.",
        "download_extension": "📥 Scarica Estensione",
        "never": "Mai",
        "views": "visualizzazioni",
        "completions": "completamenti"
    }
}

SUPPORTED_LANGUAGES = {"en": "🇬🇧 English", "ro": "🇷🇴 Română", "it": "🇮🇹 Italiano"}
DEFAULT_LANGUAGE = "en"

def get_current_language():
    """Get the currently selected language from session state."""
    if "language" not in st.session_state:
        st.session_state.language = DEFAULT_LANGUAGE
    return st.session_state.language

def set_language(lang_code):
    """Set the current language."""
    if lang_code in SUPPORTED_LANGUAGES:
        st.session_state.language = lang_code

def get_text(key, *args):
    """
    Get translated text for the given key.
    
    Args:
        key: Translation key
        *args: Optional format arguments for string interpolation
    
    Returns:
        Translated string or the key itself if not found
    """
    lang = get_current_language()
    translations = TRANSLATIONS.get(lang, TRANSLATIONS[DEFAULT_LANGUAGE])
    text = translations.get(key, key)
    
    if args:
        try:
            text = text.format(*args)
        except:
            pass
    
    return text

def t(key, *args):
    """Shorthand for get_text()"""
    return get_text(key, *args)

def get_supported_languages():
    """Return dictionary of supported languages."""
    return SUPPORTED_LANGUAGES

def render_language_toggle():
    """Render a language toggle in the sidebar."""
    current = get_current_language()
    
    # Create horizontal radio buttons
    languages = list(SUPPORTED_LANGUAGES.keys())
    labels = list(SUPPORTED_LANGUAGES.values())
    
    current_index = languages.index(current) if current in languages else 0
    
    selected = st.sidebar.radio(
        "🌐 Language",
        languages,
        index=current_index,
        format_func=lambda x: SUPPORTED_LANGUAGES[x],
        horizontal=True,
        key="lang_toggle",
        label_visibility="collapsed"
    )
    
    if selected != current:
        set_language(selected)
        st.rerun()
