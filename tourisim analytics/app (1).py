import streamlit as st, pandas as pd, numpy as np, plotly.express as px, plotly.graph_objects as go
st.set_page_config(page_title="Tourism & Hospitality Insights",page_icon="🌍",layout="wide")
st.markdown("""<style>
.block-container{max-width:1450px;padding-top:1.4rem}
[data-testid="stSidebar"]{background:#f4f7fa}
.hero{padding:22px 26px;border:1px solid #e2e9ef;border-radius:16px;background:linear-gradient(110deg,#f4f8fb,#edf6f4);margin-bottom:18px}
.hero h1{color:#18334e;margin:0;font-size:2rem}.hero p{color:#64778a;margin:6px 0 0}
.kpi{background:white;border:1px solid #e1e8ee;border-radius:14px;padding:15px;min-height:105px}
.kl{color:#68798a;font-size:.82rem}.kv{font-size:1.65rem;font-weight:750;color:#18334e;margin-top:5px}.kn{font-size:.75rem;color:#168b83}
</style>""",unsafe_allow_html=True)

@st.cache_data
def demo():
    rng=np.random.default_rng(19); dates=pd.date_range("2024-01-01","2025-12-01",freq="MS")
    dests=["Chennai","Ooty","Kodaikanal","Madurai","Coimbatore","Goa","Jaipur","Kerala"]
    season={1:1.05,2:.95,3:.92,4:1,5:1.10,6:1.12,7:1.15,8:1.18,9:1.04,10:1.10,11:1.22,12:1.35}
    t=[];h=[]
    for i,d in enumerate(dests):
        base=16000+i*2100; rooms=240+i*28
        for dt in dates:
            n=max(1000,int(base*season[dt.month]*(1+rng.normal(0,.10))))
            intl=int(n*(.08+i*.006)); occ=float(np.clip(48+season[dt.month]*18+i*1.1+rng.normal(0,5),25,96)); occupied=round(rooms*occ/100)
            t.append([dt,d,n,n-intl,intl]);h.append([dt,d,rooms,occupied,round(occupied/rooms*100,1)])
    return pd.DataFrame(t,columns=["Date","Destination","Tourist Arrivals","Domestic Arrivals","International Arrivals"]),pd.DataFrame(h,columns=["Date","Destination","Total Rooms","Occupied Rooms","Occupancy Rate"])

def normalize(raw,kind):
    x=raw.copy(); x.columns=[str(c).strip() for c in x.columns]
    lookup={c.lower().replace("_"," ").replace("-"," "):c for c in x.columns}
    def col(*names):
        return next((lookup[n.lower().replace("_"," ")] for n in names if n.lower().replace("_"," ") in lookup),None)
    dc=col("Date","Month","Period"); lc=col("Destination","Place","City","Location","Region")
    if dc: x["Date"]=pd.to_datetime(x[dc],errors="coerce")
    if lc: x["Destination"]=x[lc].astype(str).str.strip().str.title()
    if kind=="tour":
        for target,names in [("Tourist Arrivals",("Tourist Arrivals","Arrivals","Visitors","Total Tourists")),("Domestic Arrivals",("Domestic Arrivals","Domestic")),("International Arrivals",("International Arrivals","International"))]:
            c=col(*names)
            if c: x[target]=pd.to_numeric(x[c],errors="coerce")
        req=["Date","Destination","Tourist Arrivals"]
    else:
        for target,names in [("Total Rooms",("Total Rooms","Rooms","Available Rooms")),("Occupied Rooms",("Occupied Rooms","Rooms Occupied")),("Occupancy Rate",("Occupancy Rate","Occupancy","Occupancy %"))]:
            c=col(*names)
            if c: x[target]=pd.to_numeric(x[c],errors="coerce")
        if "Occupancy Rate" not in x and {"Total Rooms","Occupied Rooms"}<=set(x):
            x["Occupancy Rate"]=np.where(x["Total Rooms"]>0,x["Occupied Rooms"]/x["Total Rooms"]*100,np.nan)
        req=["Date","Destination"]+(["Occupancy Rate"] if "Occupancy Rate" not in x else [])
    return x,[c for c in req if c not in x]

def load_file(f):
    return pd.read_csv(f) if f.name.lower().endswith(".csv") else pd.read_excel(f)
def download(df,name,label):
    st.download_button(label,df.to_csv(index=False).encode(),name,"text/csv")
def filters(df,key):
    if df.empty:return df
    a,b,c=st.columns([1,1,1.4]); lo=pd.to_datetime(df.Date).min().date();hi=pd.to_datetime(df.Date).max().date()
    with a:s=st.date_input("From",lo,min_value=lo,max_value=hi,key=key+"s")
    with b:e=st.date_input("To",hi,min_value=lo,max_value=hi,key=key+"e")
    with c:d=st.selectbox("Destination",["All destinations"]+sorted(df.Destination.dropna().unique()),key=key+"d")
    z=df[pd.to_datetime(df.Date).dt.date.between(s,e)]
    return z if d=="All destinations" else z[z.Destination==d]
def card(label,value,note):
    st.markdown(f'<div class="kpi"><div class="kl">{label}</div><div class="kv">{value}</div><div class="kn">{note}</div></div>',unsafe_allow_html=True)

if "tour" not in st.session_state:
    st.session_state.tour,st.session_state.hotel=demo();st.session_state.demo=True
pages=["Overview Dashboard","Update Your Business Data","Tourism Analysis","Hotel Analysis","Comparative Analysis","Destination Explorer","Reports","About Project"]
with st.sidebar:
    st.markdown("## 🌍 T&H INSIGHTS");st.caption("Tourism Analytics Platform")
    page=st.radio("NAVIGATION",pages)
    st.divider();st.caption("DATA STATUS")
    st.write(f"Tourism: {len(st.session_state.tour):,} records")
    st.write(f"Hotel: {len(st.session_state.hotel):,} records")
    if st.session_state.demo: st.info("Synthetic demo data is active.")
    if st.button("Reset to demo data"):
        st.session_state.tour,st.session_state.hotel=demo();st.session_state.demo=True;st.rerun()
t=st.session_state.tour.copy();h=st.session_state.hotel.copy()

if page=="Overview Dashboard":
    st.markdown('<div class="hero"><h1>Tourism & Hospitality Insights</h1><p>Explore tourist arrivals, hotel occupancy and destination performance in one place.</p></div>',unsafe_allow_html=True)
    st.caption("Decision-support analytics for tourism departments, hotel managers, travel agencies and researchers.")
    st.markdown("### Filter your view")
    # One shared filter controls both tourism and hotel metrics/charts.
    date_min=min(pd.to_datetime(t["Date"]).min().date(),pd.to_datetime(h["Date"]).min().date())
    date_max=max(pd.to_datetime(t["Date"]).max().date(),pd.to_datetime(h["Date"]).max().date())
    f1,f2,f3=st.columns([1,1,1.5])
    with f1: start_date=st.date_input("From",date_min,min_value=date_min,max_value=date_max,key="overview_from")
    with f2: end_date=st.date_input("To",date_max,min_value=date_min,max_value=date_max,key="overview_to")
    destinations=sorted(set(t["Destination"].dropna()) | set(h["Destination"].dropna()))
    with f3: selected_destination=st.selectbox("Destination",["All destinations"]+destinations,key="overview_destination")
    tf=t[pd.to_datetime(t["Date"]).dt.date.between(start_date,end_date)].copy()
    hf=h[pd.to_datetime(h["Date"]).dt.date.between(start_date,end_date)].copy()
    if selected_destination!="All destinations":
        tf=tf[tf["Destination"]==selected_destination]
        hf=hf[hf["Destination"]==selected_destination]
    vals=[f'{tf["Tourist Arrivals"].sum():,.0f}',f'{hf["Occupancy Rate"].mean():.1f}%' if len(hf) else "—",str(tf.Destination.nunique()),f"{len(tf):,}"]
    cols=st.columns(4)
    for c,(lab,val) in zip(cols,zip(["Total tourist arrivals","Average hotel occupancy","Destinations covered","Tourism records"],vals)):
        with c:card(lab,val,"Based on selected filters")
    a,b=st.columns(2)
    with a:
        st.markdown("#### Tourist arrivals over time")
        if len(tf):st.plotly_chart(px.line(tf.set_index("Date").resample("MS")["Tourist Arrivals"].sum().reset_index(),x="Date",y="Tourist Arrivals",markers=True,template="plotly_white"),use_container_width=True)
        else:st.info("No matching tourism data.")
    with b:
        st.markdown("#### Hotel occupancy over time")
        if len(hf):
            f=px.line(hf.set_index("Date").resample("MS")["Occupancy Rate"].mean().reset_index(),x="Date",y="Occupancy Rate",markers=True,template="plotly_white");f.update_yaxes(range=[0,100],title="Occupancy (%)");st.plotly_chart(f,use_container_width=True)
        else:st.info("No matching hotel data.")
    if len(tf):
        top=tf.groupby("Destination",as_index=False)["Tourist Arrivals"].sum().nlargest(5,"Tourist Arrivals")
        st.markdown("#### Top destinations");st.plotly_chart(px.bar(top,x="Tourist Arrivals",y="Destination",orientation="h",template="plotly_white"),use_container_width=True)

elif page=="Update Your Business Data":
    st.header("Update Your Business Data")
    st.write("Use this page when you want to refresh the dashboard with your latest monthly tourism or hotel performance figures. You do not need to edit the charts manually — upload your report and the platform updates the analysis.")
    st.info("For hotel teams: upload a monthly room summary containing the reporting date, destination, total rooms and occupied rooms. The platform calculates the occupancy percentage automatically.")
    with st.expander("What should my hotel report contain?", expanded=True):
        st.markdown("**Required fields**\n- **Date:** reporting month (for example, 2026-10-01)\n- **Destination:** city or property location\n- **Total Rooms:** rooms available for sale\n- **Occupied Rooms:** rooms sold/occupied during the reporting period")
        template=pd.DataFrame({"Date":["2026-10-01"],"Destination":["Chennai"],"Total Rooms":[100],"Occupied Rooms":[72]})
        st.download_button("Download hotel report template",template.to_csv(index=False).encode(),"hotel_monthly_report_template.csv","text/csv")
        st.caption("You can also upload an existing report if it contains these fields, or an Occupancy Rate column (0–100).")
    st.markdown("### Update hotel performance")
    hf=st.file_uploader("Choose your hotel monthly report (CSV or Excel)",type=["csv","xlsx"],key="hu")
    if hf:
        try:
            raw=load_file(hf);x,missing=normalize(raw,"hotel")
            if missing:
                st.error("We couldn't identify these required fields: "+", ".join(missing)+". Please use the template above.")
            else:
                x=x.dropna(subset=["Date","Destination"])
                if "Occupancy Rate" in x:
                    bad=~x["Occupancy Rate"].between(0,100)
                    if bad.any(): st.warning(f"{int(bad.sum())} rows have occupancy outside 0–100% and should be checked.")
                st.session_state.hotel=x;st.session_state.demo=False
                st.success(f"Hotel report updated successfully: {len(x):,} reporting records are now available to the dashboard.")
        except Exception as e: st.error(f"We couldn't read this file: {e}")
    st.markdown("### Update tourism arrivals (optional)")
    st.caption("Tourism teams can upload monthly visitor statistics here. Hotel managers can skip this step and use the hotel performance dashboard.")
    tf=st.file_uploader("Choose tourism arrivals report (CSV or Excel)",type=["csv","xlsx"],key="tu")
    if tf:
        try:
            raw=load_file(tf);x,missing=normalize(raw,"tour")
            if missing: st.error("We couldn't identify these required fields: "+", ".join(missing)+". Required: Date, Destination and Tourist Arrivals.")
            else:
                x=x.dropna(subset=["Date","Destination","Tourist Arrivals"]);st.session_state.tour=x;st.session_state.demo=False
                st.success(f"Tourism report updated successfully: {len(x):,} reporting records loaded.")
        except Exception as e: st.error(f"We couldn't read this file: {e}")
    st.caption("Your dashboard and reports will use the latest successfully uploaded datasets. Existing analysis is not changed until a valid file is uploaded.")

elif page=="Data Cleaning":
    st.header("Data Cleaning & Validation")
    for label,df in [("Tourism",t),("Hotel",h)]:
        st.subheader(label);a,b,c,d=st.columns(4)
        a.metric("Rows",f"{len(df):,}");b.metric("Missing cells",int(df.isna().sum().sum()));c.metric("Duplicate rows",int(df.duplicated().sum()))
        invalid=0
        if "Tourist Arrivals" in df:invalid+=int((df["Tourist Arrivals"]<0).sum())
        if "Occupancy Rate" in df:invalid+=int((~df["Occupancy Rate"].between(0,100)).sum())
        if {"Total Rooms","Occupied Rooms"}<=set(df):invalid+=int((df["Occupied Rooms"]>df["Total Rooms"]).sum())
        d.metric("Invalid values",invalid);st.dataframe(df.isna().sum().rename("Missing values").to_frame(),use_container_width=True)
    st.warning("Issues are flagged for review. Original uploaded records are not silently overwritten.")
    if st.button("Prepare cleaned copies"):
        ct=t.drop_duplicates().copy();ch=h.drop_duplicates().copy()
        if "Tourist Arrivals" in ct:ct=ct[ct["Tourist Arrivals"].isna()|(ct["Tourist Arrivals"]>=0)]
        if "Occupancy Rate" in ch:ch=ch[ch["Occupancy Rate"].isna()|ch["Occupancy Rate"].between(0,100)]
        if {"Total Rooms","Occupied Rooms"}<=set(ch):ch=ch[ch["Occupied Rooms"].isna()|ch["Total Rooms"].isna()|(ch["Occupied Rooms"]<=ch["Total Rooms"])]
        st.session_state.ct=ct;st.session_state.ch=ch;st.success(f"Prepared {len(ct):,} tourism and {len(ch):,} hotel rows.")
    if "ct" in st.session_state:
        a,b=st.columns(2);a.download_button("Download cleaned tourism",st.session_state.ct.to_csv(index=False).encode(),"cleaned_tourism.csv");b.download_button("Download cleaned hotel",st.session_state.ch.to_csv(index=False).encode(),"cleaned_hotel.csv")

elif page=="Tourism Analysis":
    st.header("Tourism Arrivals Analysis");x=filters(t,"ta")
    if len(x):
        st.metric("Arrivals in selected view",f'{x["Tourist Arrivals"].sum():,.0f}')
        a,b=st.columns(2)
        a.plotly_chart(px.line(x.set_index("Date").resample("MS")["Tourist Arrivals"].sum().reset_index(),x="Date",y="Tourist Arrivals",markers=True,title="Monthly arrivals",template="plotly_white"),use_container_width=True)
        b.plotly_chart(px.bar(x.groupby("Destination",as_index=False)["Tourist Arrivals"].sum(),x="Tourist Arrivals",y="Destination",orientation="h",title="Arrivals by destination",template="plotly_white"),use_container_width=True)
        if {"Domestic Arrivals","International Arrivals"}<=set(x):
            z=x[["Domestic Arrivals","International Arrivals"]].sum().rename_axis("Category").reset_index(name="Arrivals");st.plotly_chart(px.pie(z,names="Category",values="Arrivals",hole=.45,title="Domestic vs international"),use_container_width=True)
        st.dataframe(x,use_container_width=True);download(x,"filtered_tourism.csv","Download filtered tourism")
    else:st.info("No data for selected filters.")

elif page=="Hotel Analysis":
    st.header("Hotel Performance & Room Planning")
    st.write("A practical view for hotel managers to monitor room demand, identify busy periods and plan room operations.")
    x=filters(h,"ha")
    if len(x):
        avg=float(x["Occupancy Rate"].mean())
        total_rooms=float(x["Total Rooms"].sum()) if "Total Rooms" in x else np.nan
        occupied=float(x["Occupied Rooms"].sum()) if "Occupied Rooms" in x else np.nan
        vacant=max(total_rooms-occupied,0) if pd.notna(total_rooms) and pd.notna(occupied) else np.nan
        peak=x.loc[x["Occupancy Rate"].idxmax()]
        a,b,c,d=st.columns(4)
        a.metric("Average occupancy",f"{avg:.1f}%")
        b.metric("Highest recorded occupancy",f"{x['Occupancy Rate'].max():.1f}%")
        c.metric("Rooms occupied",f"{occupied:,.0f}" if pd.notna(occupied) else "Not provided")
        d.metric("Rooms not occupied",f"{vacant:,.0f}" if pd.notna(vacant) else "Not provided")
        if avg>=80: st.success("High demand: occupancy is strong. Review staffing, housekeeping schedules and room readiness for peak periods.")
        elif avg>=60: st.info("Moderate demand: monitor booking pace and plan staff schedules around the monthly trend.")
        else: st.warning("Lower occupancy: review demand patterns and consider targeted promotions or partnerships during quieter periods.")
        st.markdown("### Occupancy trend")
        monthly=x.set_index("Date").resample("MS")["Occupancy Rate"].mean().reset_index()
        fig=px.line(monthly,x="Date",y="Occupancy Rate",markers=True,template="plotly_white",labels={"Occupancy Rate":"Occupancy (%)","Date":"Month"})
        fig.update_yaxes(range=[0,100]);st.plotly_chart(fig,use_container_width=True)
        st.markdown("### Destination / property comparison")
        comp=x.groupby("Destination",as_index=False).agg( average_occupancy=("Occupancy Rate","mean"), highest_occupancy=("Occupancy Rate","max"))
        st.plotly_chart(px.bar(comp.sort_values("average_occupancy"),x="average_occupancy",y="Destination",orientation="h",labels={"average_occupancy":"Average occupancy (%)"},template="plotly_white"),use_container_width=True)
        st.markdown("### Busiest reporting period")
        st.write(f"**{pd.to_datetime(peak['Date']).strftime('%B %Y')} – {peak['Destination']}** recorded the highest occupancy ({peak['Occupancy Rate']:.1f}%). Use this period as a reference when planning staffing and room availability.")
        with st.expander("View underlying hotel records"):
            st.dataframe(x,use_container_width=True)
        download(x,"hotel_performance_report.csv","Download hotel performance report")
        st.caption("Planning indicators are based on the uploaded reporting data; they are not live reservations or real-time room availability.")
    else: st.info("No hotel records match the selected filters. Update the hotel report in 'Update Your Business Data'.")

elif page=="Comparative Analysis":
    st.header("Tourism Arrivals vs Hotel Occupancy")
    common=set(t.Destination.dropna())&set(h.Destination.dropna())
    if not common:st.warning("No matching destination names. Comparative analysis requires matching destinations.")
    else:
        tt=t[t.Destination.isin(common)].copy();hh=h[h.Destination.isin(common)].copy()
        tt["Month"]=pd.to_datetime(tt.Date).dt.to_period("M").astype(str);hh["Month"]=pd.to_datetime(hh.Date).dt.to_period("M").astype(str)
        m=tt.groupby(["Destination","Month"],as_index=False)["Tourist Arrivals"].sum().merge(hh.groupby(["Destination","Month"],as_index=False)["Occupancy Rate"].mean(),on=["Destination","Month"])
        if not len(m):st.warning("No overlapping destination-month periods.")
        else:
            d=st.selectbox("Destination",["All destinations"]+sorted(m.Destination.unique()));v=m if d=="All destinations" else m[m.Destination==d]
            fig=go.Figure();fig.add_trace(go.Scatter(x=v.Month,y=v["Tourist Arrivals"],name="Tourist arrivals",mode="lines+markers"));fig.add_trace(go.Scatter(x=v.Month,y=v["Occupancy Rate"],name="Occupancy rate (%)",mode="lines+markers",yaxis="y2"))
            fig.update_layout(template="plotly_white",title="Matched monthly trends",yaxis=dict(title="Arrivals"),yaxis2=dict(title="Occupancy (%)",overlaying="y",side="right",range=[0,100]),height=430);st.plotly_chart(fig,use_container_width=True)
            st.plotly_chart(px.scatter(v,x="Tourist Arrivals",y="Occupancy Rate",color="Destination",hover_data=["Month"],title="Arrivals vs occupancy",template="plotly_white"),use_container_width=True)
            if len(v)>=3 and v["Tourist Arrivals"].nunique()>1 and v["Occupancy Rate"].nunique()>1:st.metric("Pearson correlation",f'{v[["Tourist Arrivals","Occupancy Rate"]].corr().iloc[0,1]:.2f}',help="Association does not establish causation.")
            else:st.info("More matched observations are needed for correlation.")
            st.dataframe(m,use_container_width=True);download(m,"comparative_analysis.csv","Download matched comparison")

elif page=="Destination Explorer":
    st.header("Destination Explorer");common=sorted(set(t.Destination.dropna())&set(h.Destination.dropna()))
    if not common:st.info("Upload datasets with matching destination names.")
    else:
        d=st.selectbox("Choose a destination",common);tt=t[t.Destination==d];hh=h[h.Destination==d]
        a,b,c=st.columns(3);a.metric("Tourist arrivals",f'{tt["Tourist Arrivals"].sum():,.0f}');b.metric("Average occupancy",f'{hh["Occupancy Rate"].mean():.1f}%');c.metric("Tourism records",len(tt))
        a,b=st.columns(2);a.plotly_chart(px.area(tt.set_index("Date").resample("MS")["Tourist Arrivals"].sum().reset_index(),x="Date",y="Tourist Arrivals",title=f"{d}: arrivals"),use_container_width=True);b.plotly_chart(px.line(hh.set_index("Date").resample("MS")["Occupancy Rate"].mean().reset_index(),x="Date",y="Occupancy Rate",markers=True,title=f"{d}: occupancy"),use_container_width=True)
        st.caption("Views are based only on available uploaded records; no map is fabricated when geographic coordinates are absent.")

elif page=="Reports":
    st.header("Reports & Downloads");a,b=st.columns(2)
    with a:st.subheader("Tourism");download(t,"tourism_arrivals_report.csv","Download tourism dataset");st.subheader("Hotel");download(h,"hotel_occupancy_report.csv","Download hotel dataset")
    with b:
        summary=pd.DataFrame([["Tourism records",len(t)],["Total arrivals",t["Tourist Arrivals"].sum()],["Tourism destinations",t.Destination.nunique()],["Hotel records",len(h)],["Average occupancy",h["Occupancy Rate"].mean()],["Hotel destinations",h.Destination.nunique()]],columns=["Indicator","Value"])
        st.subheader("Platform summary");st.dataframe(summary,use_container_width=True);download(summary,"platform_summary.csv","Download summary CSV")
    st.caption("CSV exports are included in this lightweight local build.")

else:
    st.header("About the Project")
    st.markdown('<div class="hero"><h1>Development of a Tourism Arrivals and Hotel Occupancy Visualization Platform</h1><p>An interactive decision-support platform for tourism and hospitality data.</p></div>',unsafe_allow_html=True)
    st.subheader("Problem statement");st.write("Tourism arrivals and hotel occupancy data are often stored separately. Manual comparison makes it difficult to identify destination-wise patterns and seasonal demand.")
    st.subheader("Proposed solution");st.write("A centralized dashboard to upload, validate, clean, analyse and visualize both datasets, including comparisons where destination and month match.")
    st.subheader("Modules");st.markdown("1. Data Import & Management\n2. Data Validation and Preprocessing\n3. Tourism, Hotel and Comparative Analytics\n4. Destination Exploration and Reporting")
    st.subheader("Intended users");st.write("Tourism departments • Hotel owners and managers • Travel agencies • Tourism planners • Researchers and students")
    st.subheader("Technology stack");st.write("Python • Streamlit • Pandas • NumPy • Plotly • OpenPyXL")
    st.caption("Academic prototype. Built-in sample records are synthetic demo data, not official tourism statistics.")
