import streamlit as st

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from apis.display import crime_info

st.divider()

st.header('Crime Information')
tab1, tab2, tab3, tab4 = st.tabs(['Overall', 'Date', 'Crime Type', 'Victim'])
with tab1:
    crime_info(3539618, 'overall')
with tab2:
    crime_info(3539618, 'date')
with tab3:
    crime_info(3539618, 'crime_type')
with tab4:
    crime_info(3539618, 'victim')