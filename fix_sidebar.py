with open('streamlit_app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove lines 471-479 (Brand/Logo Section) and replace with simple header
new_lines = lines[:470] + [
    '    # Clean Navigation Header\n',
    '    st.markdown(f\'<p style="color: {sidebar_text}; font-weight: 700; margin-top: 0.5rem; margin-bottom: 1rem; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; padding-left: 0.5rem;">📋 Menu</p>\', unsafe_allow_html=True)\n',
    '    \n'
] + lines[480:]

with open('streamlit_app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Removed unwanted brand section from sidebar")
