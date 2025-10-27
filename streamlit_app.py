import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
import time

# Load API base URL from secrets or use default
try:
    API_BASE = st.secrets.get('API_BASE', 'http://localhost:8000')
except FileNotFoundError:
    API_BASE = 'http://localhost:8000'

# Configure session timeout and connection pooling
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=20)
session.mount('http://', adapter)
session.mount('https://', adapter)

st.set_page_config(page_title="Voter Analysis Dashboard", layout="wide")
st.title('🗳️ Voter Analysis Dashboard')

tab = st.sidebar.selectbox('View', ['📊 Summary','👥 Voters','📤 Upload PDF','➕ Add Voter', '🔍 Search & Filter'])

if tab == '📊 Summary':
    with st.spinner('Loading summary data...'):
        resp = session.get(f'{API_BASE}/voters/summary', timeout=5)
    data = resp.json()
    df = pd.DataFrame(data)
    st.subheader('Total voters by constituency')
    if not df.empty:
        fig = px.bar(df, x='constituency', y='count', title='Voters by Constituency')
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    
    with col1:
        gr = session.get(f'{API_BASE}/voters/gender-ratio', timeout=5).json()
        labels = list(gr.keys())
        values = list(gr.values())
        fig2 = px.pie(values=values, names=labels, title='Gender Distribution')
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        ages = session.get(f'{API_BASE}/voters/age-distribution', timeout=5).json()
        adf = pd.DataFrame(list(ages.items()), columns=['age_range','count'])
        fig3 = px.bar(adf, x='age_range', y='count', title='Age Distribution', color='count')
        st.plotly_chart(fig3, use_container_width=True)

elif tab == '👥 Voters':
    # Fetch constituency options for filter
    if 'constituency_options' not in st.session_state:
        try:
            resp_summary = session.get(f'{API_BASE}/voters/summary', timeout=5)
            if resp_summary.status_code == 200:
                summary_data = resp_summary.json()
                st.session_state.constituency_options = ['All'] + [item['constituency'] for item in summary_data if item.get('constituency')]
            else:
                st.session_state.constituency_options = ['All']
        except:
            st.session_state.constituency_options = ['All']
    
    # Add advanced filters in expander
    with st.expander("🔍 Advanced Filters", expanded=False):
        filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
        
        with filter_col1:
            filter_constituency = st.multiselect('Constituency', options=st.session_state.constituency_options, default=['All'])
        
        with filter_col2:
            filter_gender = st.multiselect('Gender', options=['All', 'M', 'F'], default=['All'])
        
        with filter_col3:
            filter_age_min = st.number_input('Min Age', min_value=0, max_value=150, value=0)
            filter_age_max = st.number_input('Max Age', min_value=0, max_value=150, value=150)
        
        with filter_col4:
            filter_booth = st.text_input('Booth No (partial match)', value='')
            filter_voting_status = st.selectbox('Voting Status', ['All', 'Voted', 'Not Voted'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        page = st.number_input('Page', min_value=0, value=0)
    with col2:
        limit = st.number_input('Page size', min_value=10, max_value=100, value=50)
    with col3:
        search_query = st.text_input('🔍 Quick Search', placeholder='Name, constituency, booth...')
    
    # If search query is provided, use search endpoint
    if search_query and search_query.strip():
        with st.spinner('Searching...'):
            resp = session.get(f'{API_BASE}/voters/search', params={'q': search_query, 'limit': 500}, timeout=10)
            if resp.status_code == 200:
                voters = resp.json()
                st.info(f'Found {len(voters)} matching voters')
            else:
                st.error(f'Search error: {resp.json()}')
                voters = []
    else:
        # Normal pagination
        resp = session.get(f'{API_BASE}/voters', params={'skip': page*limit, 'limit': limit}, timeout=10)
        if resp.status_code == 200:
            voters = resp.json()
        else:
            st.error(f'Error fetching voters: {resp.json()}')
            voters = []
    
    df = pd.DataFrame(voters)
    
    if not df.empty:
        # Apply multiple filters
        filtered_df = df.copy()
        
        # Filter by constituency
        if 'All' not in filter_constituency and filter_constituency:
            filtered_df = filtered_df[filtered_df['constituency'].isin(filter_constituency)]
        
        # Filter by gender
        if 'All' not in filter_gender and filter_gender:
            filtered_df = filtered_df[filtered_df['gender'].isin(filter_gender)]
        
        # Filter by age range
        if filter_age_min > 0 or filter_age_max < 150:
            filtered_df = filtered_df[
                (filtered_df['age'].fillna(0) >= filter_age_min) & 
                (filtered_df['age'].fillna(0) <= filter_age_max)
            ]
        
        # Filter by booth number
        if filter_booth:
            filtered_df = filtered_df[filtered_df['booth_no'].str.contains(filter_booth, case=False, na=False)]
        
        # Filter by voting status
        if filter_voting_status == 'Voted':
            filtered_df = filtered_df[filtered_df['vote'].apply(lambda x: str(x).lower() in ['true', '1', 'yes'])]
        elif filter_voting_status == 'Not Voted':
            filtered_df = filtered_df[~filtered_df['vote'].apply(lambda x: str(x).lower() in ['true', '1', 'yes'])]
        
        df = filtered_df
        
        # Display summary stats
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric('Total Records', len(df))
        with col2:
            st.metric('Average Age', f"{df['age'].replace([None], 0).mean():.1f}")
        with col3:
            male_count = (df['gender'] == 'M').sum()
            st.metric('Males', male_count)
        with col4:
            female_count = (df['gender'] == 'F').sum()
            st.metric('Females', female_count)
        with col5:
            voted_count = df['vote'].apply(lambda x: str(x).lower() in ['true', '1', 'yes']).sum()
            st.metric('Voting Count', voted_count)
        
        st.divider()
        
        # Add Save All button
        col_header, col_save_all = st.columns([4, 1])
        with col_header:
            st.subheader(f'📋 Voters List (showing {len(df)} records)')
        with col_save_all:
            if st.button('💾 Save All Changes', use_container_width=True, type='primary'):
                with st.spinner('Saving all changes...'):
                    # Collect all updates
                    updates = []
                    for idx, row in df.iterrows():
                        vote_key = f"vote_{row['id']}"
                        if vote_key in st.session_state:
                            updates.append((row['id'], st.session_state[vote_key]))
                    
                    # Parallel execution for faster saves
                    def save_voter(voter_data):
                        voter_id, vote_status = voter_data
                        try:
                            r = session.put(f'{API_BASE}/voters/{voter_id}', 
                                          json={'vote': vote_status}, 
                                          timeout=5)
                            return r.status_code == 200
                        except:
                            return False
                    
                    success_count = 0
                    error_count = 0
                    
                    # Use ThreadPoolExecutor for parallel requests
                    with ThreadPoolExecutor(max_workers=10) as executor:
                        results = list(executor.map(save_voter, updates))
                        success_count = sum(results)
                        error_count = len(results) - success_count
                    
                    if error_count == 0:
                        st.toast(f'✅ All {success_count} records saved successfully!', icon='✔️')
                    else:
                        st.toast(f'⚠️ Saved {success_count} records, {error_count} errors', icon='⚠️')
        
        # Display column headers
        col_id, col_name, col_age, col_gender, col_constituency, col_booth, col_address, col_vote = st.columns([0.6, 1.8, 0.7, 0.6, 1.2, 0.8, 1.5, 0.8])
        with col_id:
            st.markdown("**ID**")
        with col_name:
            st.markdown("**Name**")
        with col_age:
            st.markdown("**Age**")
        with col_gender:
            st.markdown("**Gender**")
        with col_constituency:
            st.markdown("**Constituency**")
        with col_booth:
            st.markdown("**Booth**")
        with col_address:
            st.markdown("**Address**")
        with col_vote:
            st.markdown("**Voted**")
        
        st.markdown("---")
        
        # Display inline editing rows
        for idx, row in df.iterrows():
            col_id, col_name, col_age, col_gender, col_constituency, col_booth, col_address, col_vote = st.columns([0.6, 1.8, 0.7, 0.6, 1.2, 0.8, 1.5, 0.8])
            
            with col_id:
                st.text(f"#{row['id']}")
            
            # Read-only fields (displayed as text)
            with col_name:
                st.text(row.get('name', ''))
            
            with col_age:
                st.text(str(int(row.get('age', 0)) if row.get('age') and not (isinstance(row.get('age'), float) and pd.isna(row.get('age'))) else 0))
            
            with col_gender:
                st.text(row.get('gender', ''))
            
            with col_constituency:
                st.text(row.get('constituency', ''))
            
            with col_booth:
                st.text(row.get('booth_no', ''))
            
            with col_address:
                st.text(row.get('address', ''))
            
            # Editable vote column - Use session state to track changes
            with col_vote:
                vote_key = f"vote_{row['id']}"
                if vote_key not in st.session_state:
                    vote_value = row.get('vote', False)
                    if isinstance(vote_value, str):
                        vote_value = vote_value.lower() in ['true', '1', 'yes']
                    st.session_state[vote_key] = bool(vote_value)
                
                new_vote = st.checkbox('✓', value=st.session_state[vote_key], key=vote_key, label_visibility='collapsed')
    else:
        st.info('No voters found')

elif tab == '📤 Upload PDF':
    st.subheader('Upload PDF with Voter Data')
    st.info('📋 Supported formats: PDF files with tables containing voter information')
    
    uploaded = st.file_uploader('Upload PDF', type=['pdf'])
    if uploaded:
        with st.spinner('Processing PDF...'):
            files = {'file': (uploaded.name, uploaded.getvalue(), 'application/pdf')}
            r = session.post(f'{API_BASE}/upload_pdf', files=files, timeout=60)
            if r.status_code == 200:
                st.success('✅ PDF uploaded and processed successfully!')
                st.json(r.json())
            else:
                st.error(f'❌ Error: {r.json()}')

elif tab == '➕ Add Voter':
    st.subheader('Add New Voter')
    with st.form('add_voter_form'):
        name = st.text_input('Full Name *')
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input('Age', min_value=18, max_value=130, value=30)
        with col2:
            gender = st.selectbox('Gender', ['M', 'F'])
        
        constituency = st.text_input('Constituency *')
        booth_no = st.text_input('Booth No *')
        address = st.text_area('Address')
        
        submitted = st.form_submit_button('✅ Create Voter', use_container_width=True)
        if submitted:
            if not name or not constituency or not booth_no:
                st.error('❌ Please fill in all required fields (marked with *)')
            else:
                payload = {
                    'name': name,
                    'age': age,
                    'gender': gender,
                    'constituency': constituency,
                    'booth_no': booth_no,
                    'address': address
                }
                r = session.post(f'{API_BASE}/voters', json=payload, timeout=5)
                if r.status_code == 200:
                    st.success('✅ Voter created successfully!')
                    st.json(r.json())
                else:
                    st.error(f'❌ Error: {r.json()}')

elif tab == '🔍 Search & Filter':
    st.subheader('Search & Filter Voters')
    
    search_type = st.selectbox('Select operation:', [
        'Full Text Search', 
        'Find Duplicates by Name',
        'Multi-Filter Search',
        'Filter by Constituency', 
        'Filter by Gender', 
        'Filter by Age Range'
    ])
    
    if search_type == 'Full Text Search':
        col1, col2 = st.columns([3, 1])
        with col1:
            query = st.text_input('Search by name, constituency, or booth number')
        with col2:
            search_limit = st.number_input('Max Results', min_value=10, max_value=1000, value=100)
        
        if query:
            with st.spinner('Searching...'):
                r = session.get(f'{API_BASE}/voters/search', params={'q': query, 'limit': search_limit}, timeout=10)
                if r.status_code == 200:
                    results = r.json()
                    st.success(f'Found {len(results)} results')
                    if results:
                        df = pd.DataFrame(results)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.error(f'Error: {r.json()}')
    
    elif search_type == 'Find Duplicates by Name':
        st.info('🔍 This will find all voters with duplicate names (case-insensitive)')
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button('🔎 Find Duplicates', type='primary', use_container_width=True):
                with st.spinner('Searching for duplicates...'):
                    # Fetch all voters
                    r = session.get(f'{API_BASE}/voters', params={'skip': 0, 'limit': 10000}, timeout=30)
                    if r.status_code == 200:
                        all_voters = r.json()
                        df = pd.DataFrame(all_voters)
                        
                        if not df.empty:
                            # Find duplicates based on name (case-insensitive)
                            df['name_lower'] = df['name'].str.lower().str.strip()
                            duplicates = df[df.duplicated(subset=['name_lower'], keep=False)].copy()
                            duplicates = duplicates.sort_values('name_lower')
                            duplicates = duplicates.drop(columns=['name_lower'])
                            
                            if not duplicates.empty:
                                st.warning(f'⚠️ Found {len(duplicates)} duplicate records ({len(duplicates["name"].unique())} unique names)')
                                
                                # Show summary
                                duplicate_summary = duplicates.groupby(duplicates['name'].str.lower()).size().reset_index(name='count')
                                duplicate_summary.columns = ['Name', 'Occurrences']
                                duplicate_summary = duplicate_summary.sort_values('Occurrences', ascending=False)
                                
                                st.subheader('📊 Duplicate Names Summary')
                                st.dataframe(duplicate_summary, use_container_width=True, hide_index=True)
                                
                                st.subheader('📋 All Duplicate Records')
                                st.dataframe(duplicates, use_container_width=True, hide_index=True)
                                
                                # Export option
                                csv = duplicates.to_csv(index=False)
                                st.download_button(
                                    label='📥 Download Duplicates as CSV',
                                    data=csv,
                                    file_name='duplicate_voters.csv',
                                    mime='text/csv'
                                )
                            else:
                                st.success('✅ No duplicate names found!')
                        else:
                            st.info('No voters found in database')
                    else:
                        st.error(f'Error fetching voters: {r.json()}')
        
        with col2:
            st.metric('Status', 'Ready')
    
    elif search_type == 'Multi-Filter Search':
        st.info('🎯 Apply multiple filters simultaneously')
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_gender = st.selectbox('Gender', ['All', 'M', 'F'])
            filter_constituency = st.text_input('Constituency (partial)')
        
        with col2:
            filter_age_min = st.number_input('Min Age', min_value=0, max_value=150, value=0)
            filter_age_max = st.number_input('Max Age', min_value=0, max_value=150, value=150)
        
        with col3:
            filter_booth = st.text_input('Booth No (partial)')
            filter_vote_status = st.selectbox('Voting Status', ['All', 'Voted', 'Not Voted'])
        
        if st.button('🔍 Apply Filters', type='primary'):
            with st.spinner('Filtering...'):
                # Fetch voters
                r = session.get(f'{API_BASE}/voters', params={'skip': 0, 'limit': 5000}, timeout=20)
                if r.status_code == 200:
                    results = r.json()
                    df = pd.DataFrame(results)
                    
                    if not df.empty:
                        # Apply filters
                        if filter_gender != 'All':
                            df = df[df['gender'] == filter_gender]
                        
                        if filter_constituency:
                            df = df[df['constituency'].str.contains(filter_constituency, case=False, na=False)]
                        
                        if filter_age_min > 0 or filter_age_max < 150:
                            df = df[(df['age'].fillna(0) >= filter_age_min) & (df['age'].fillna(0) <= filter_age_max)]
                        
                        if filter_booth:
                            df = df[df['booth_no'].str.contains(filter_booth, case=False, na=False)]
                        
                        if filter_vote_status == 'Voted':
                            df = df[df['vote'].apply(lambda x: str(x).lower() in ['true', '1', 'yes'])]
                        elif filter_vote_status == 'Not Voted':
                            df = df[~df['vote'].apply(lambda x: str(x).lower() in ['true', '1', 'yes'])]
                        
                        st.success(f'✅ Found {len(df)} matching voters')
                        if not df.empty:
                            st.dataframe(df, use_container_width=True, hide_index=True)
                            
                            # Export option
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label='📥 Download Results as CSV',
                                data=csv,
                                file_name='filtered_voters.csv',
                                mime='text/csv'
                            )
                        else:
                            st.info('No voters match the selected criteria')
                    else:
                        st.info('No voters found')
                else:
                    st.error(f'Error: {r.json()}')
    
    elif search_type == 'Filter by Constituency':
        col1, col2 = st.columns([3, 1])
        with col1:
            constituency = st.text_input('Enter constituency name (partial match)')
        with col2:
            const_limit = st.number_input('Max Results', min_value=10, max_value=1000, value=100)
        
        if constituency:
            with st.spinner('Filtering...'):
                r = session.get(f'{API_BASE}/voters/filter/constituency', params={'constituency': constituency, 'limit': const_limit}, timeout=10)
                if r.status_code == 200:
                    results = r.json()
                    st.success(f'Found {len(results)} voters')
                    if results:
                        df = pd.DataFrame(results)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        
                        csv = df.to_csv(index=False)
                        st.download_button('📥 Download CSV', csv, f'constituency_{constituency}.csv', 'text/csv')
                else:
                    st.error(f'Error: {r.json()}')
    
    elif search_type == 'Filter by Gender':
        col1, col2 = st.columns([3, 1])
        with col1:
            gender = st.selectbox('Select gender', ['M', 'F'])
        with col2:
            gender_limit = st.number_input('Max Results', min_value=10, max_value=1000, value=100)
        
        if st.button('🔍 Filter', type='primary'):
            with st.spinner('Filtering...'):
                r = session.get(f'{API_BASE}/voters/filter/gender', params={'gender': gender, 'limit': gender_limit}, timeout=10)
                if r.status_code == 200:
                    results = r.json()
                    st.success(f'Found {len(results)} voters')
                    if results:
                        df = pd.DataFrame(results)
                        st.dataframe(df, use_container_width=True, hide_index=True)
                        
                        csv = df.to_csv(index=False)
                        st.download_button('📥 Download CSV', csv, f'gender_{gender}.csv', 'text/csv')
                else:
                    st.error(f'Error: {r.json()}')
    
    elif search_type == 'Filter by Age Range':
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            min_age = st.number_input('Minimum age', min_value=0, max_value=150, value=18)
        with col2:
            max_age = st.number_input('Maximum age', min_value=0, max_value=150, value=80)
        with col3:
            age_limit = st.number_input('Max Results', min_value=10, max_value=1000, value=100)
        
        if st.button('🔍 Apply Filter', type='primary'):
            if min_age > max_age:
                st.error('❌ Minimum age cannot be greater than maximum age')
            else:
                with st.spinner('Filtering...'):
                    r = session.get(f'{API_BASE}/voters/filter/age-range', 
                                   params={'min_age': min_age, 'max_age': max_age, 'limit': age_limit}, timeout=10)
                    if r.status_code == 200:
                        results = r.json()
                        st.success(f'Found {len(results)} voters')
                        if results:
                            df = pd.DataFrame(results)
                            st.dataframe(df, use_container_width=True, hide_index=True)
                            
                            csv = df.to_csv(index=False)
                            st.download_button('📥 Download CSV', csv, f'age_{min_age}-{max_age}.csv', 'text/csv')
                    else:
                        st.error(f'Error: {r.json()}')
