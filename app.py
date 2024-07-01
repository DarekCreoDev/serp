import streamlit as st
import http.client
import json
import pandas as pd
import base64


# Funkcja do pobierania wyników wyszukiwania z API Serper.dev
def get_search_results(api_key, domain, keyword, language):
    conn = http.client.HTTPSConnection("google.serper.dev")
    query = f"site:{domain} {keyword}"
    if language == "Polish":
        payload = json.dumps({"q": query, "num": 100, "gl": "pl", "hl": "pl"})
    else:
        payload = json.dumps({"q": query, "num": 100})
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }
    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8")), query


# Funkcja do przetwarzania wyników wyszukiwania na DataFrame
def process_results(results, query):
    items = results.get("organic", [])
    data = []
    for item in items:
        title = item.get("title", "")
        link = item.get("link", "")
        snippet = item.get("snippet", "")
        data.append([title, link, snippet, query])
    df = pd.DataFrame(data, columns=["Tytuł", "Link", "Opis", "Zapytanie"])
    return df


# Ustawienia interfejsu Streamlit
st.title("🔍 Analizator słów kluczowych i domen")
st.write(
    "Wprowadź domeny i słowo kluczowe, aby uzyskać dane SEO i wygenerować raport 📊."
)

# Formularz do wprowadzania klucza API
st.sidebar.title("Ustawienia API")
api_key = st.sidebar.text_input("Wprowadź swój klucz API", type="password")
if st.sidebar.button("Zapisz klucz API"):
    st.session_state["api_key"] = api_key
    st.sidebar.success("Klucz API zapisany!")

# Formularz do wprowadzania danych
with st.form(key="search_form"):
    domains = st.text_area(
        "Wprowadź domeny (oddzielone przecinkami, np. allstate.com,libertymutual.com,geico.com) 🌐"
    )
    keyword = st.text_input("Wprowadź słowo kluczowe (np. ubezpieczenie samochodu) 🛡️")
    language = st.selectbox("Wybierz język", ["Polish", "English"])
    submit_button = st.form_submit_button(label="Szukaj 🔍")

# Przycisk do wyszukiwania
if submit_button:
    if "api_key" not in st.session_state:
        st.error("Proszę wprowadzić klucz API w ustawieniach.")
    else:
        with st.spinner("Pobieranie wyników wyszukiwania... ⏳"):
            all_data = []
            domain_list = [domain.strip() for domain in domains.split(",")]
            for domain in domain_list:
                st.write(f"Przetwarzanie zapytania: site:{domain} {keyword} 📄")
                results, query = get_search_results(
                    st.session_state["api_key"], domain, keyword, language
                )
                df = process_results(results, query)
                df["Domena"] = domain  # Dodanie kolumny z domeną
                all_data.append(df)

            if all_data:
                final_df = pd.concat(all_data, ignore_index=True)
                st.success("Wyszukiwanie zakończone! ✅")
                st.dataframe(final_df)

                # Przygotowanie pliku CSV
                csv = final_df.to_csv(index=False)
                b64 = base64.b64encode(
                    csv.encode()
                ).decode()  # Binarne kodowanie wyników
                href = f'<a href="data:file/csv;base64,{b64}" download="seo_report.csv">Pobierz plik CSV 📂</a>'
                st.markdown(href, unsafe_allow_html=True)
