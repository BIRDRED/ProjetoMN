from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

import pandas as pd
import streamlit as st


APP_TITLE = "Acervo Digital — Museu Nacional"
DEFAULT_CSV = Path(__file__).with_name("BaseMN_003_Sample.csv")


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
        .main-title {font-size: 2.15rem; font-weight: 750; margin-bottom: 0.1rem;}
        .subtitle {color: #666; margin-bottom: 1.2rem;}
        .record-card {
            border: 1px solid rgba(128,128,128,.25);
            border-radius: 14px;
            padding: 1rem 1.1rem;
            margin-bottom: .8rem;
            background: rgba(128,128,128,.04);
        }
        .small-label {font-size: .78rem; color: #777; text-transform: uppercase; letter-spacing: .04em;}
        .big-value {font-size: 1.08rem; font-weight: 650; margin-bottom: .45rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


def normalize_columns(columns: Iterable[str]) -> list[str]:
    return [str(c).replace("\ufeff", "").strip() for c in columns]


@st.cache_data(show_spinner=False)
def load_csv(source) -> pd.DataFrame:
    """Lê CSV tentando os formatos mais comuns no Windows e no Python."""
    last_error: Exception | None = None
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            if hasattr(source, "seek"):
                source.seek(0)
            df = pd.read_csv(source, encoding=encoding, sep=None, engine="python")
            df.columns = normalize_columns(df.columns)
            return prepare_dataframe(df)
        except Exception as exc:
            last_error = exc
    raise ValueError(f"Não foi possível ler o CSV: {last_error}")


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    date_columns = [
        "data_criacao",
        "data_modificacao_xmp",
        "data_metadados_xmp",
        "data_modificacao_arquivo",
        "catalogo_data_de_entrada_no_mn",
        "catalogo_data_de_tombamento",
        "catalogo_data_de_coleta",
        "catalogo_data_de_fabricação",
    ]
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    numeric_columns = [
        "largura_pixels", "altura_pixels", "megapixels", "tamanho_mb",
        "tamanho_kb", "tamanho_bytes", "iso", "distancia_focal",
        "quantidade_frames", "resolucao_x", "resolucao_y",
    ]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def existing_columns(df: pd.DataFrame, columns: Iterable[str]) -> list[str]:
    return [c for c in columns if c in df.columns]


def text_value(row: pd.Series, column: str, fallback: str = "Não informado") -> str:
    value = row.get(column)
    if pd.isna(value) or str(value).strip() == "":
        return fallback
    if isinstance(value, pd.Timestamp):
        return value.strftime("%d/%m/%Y")
    return str(value)


def unique_values(df: pd.DataFrame, column: str) -> list[str]:
    if column not in df.columns:
        return []
    values = df[column].dropna().astype(str).str.strip()
    values = values[values.ne("")]
    return sorted(values.unique().tolist(), key=str.casefold)


def apply_multiselect_filter(df: pd.DataFrame, column: str, selected: list[str]) -> pd.DataFrame:
    if selected and column in df.columns:
        return df[df[column].astype(str).isin(selected)]
    return df


def find_image_path(row: pd.Series, image_root: str | None) -> Path | None:
    candidates: list[Path] = []

    full_path = row.get("caminho_completo")
    if pd.notna(full_path) and str(full_path).strip():
        candidates.append(Path(str(full_path)))

    file_name = row.get("nome_arquivo")
    if image_root and pd.notna(file_name) and str(file_name).strip():
        candidates.append(Path(image_root) / str(file_name))

    relative = row.get("pasta_relativa")
    if image_root and pd.notna(relative) and pd.notna(file_name):
        candidates.append(Path(image_root) / str(relative) / str(file_name))

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def format_size_mb(value) -> str:
    if pd.isna(value):
        return "—"
    return f"{float(value):,.2f} MB".replace(",", "X").replace(".", ",").replace("X", ".")


st.markdown(f'<div class="main-title">🏛️ {APP_TITLE}</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Consulta, exploração e visualização dos registros catalográficos e dos metadados das imagens.</div>',
    unsafe_allow_html=True,
)


# Caminho fixo para a pasta MN_003
IMAGE_ROOT_DEFAULT = r"C:\Users\Gustavo\Documents\Projetos Mestrado\Projeto A Queda do Céu\MN_003"
image_root_SRC = IMAGE_ROOT_DEFAULT

with st.sidebar:
    st.header("Base de dados")
    uploaded_file = st.file_uploader("Selecione um arquivo CSV", type=["csv"])

IMAGE_ROOT_DEFAULT = r"C:\Users\Gustavo\Documents\Projetos Mestrado\Projeto A Queda do Céu\MN_003"
image_root = IMAGE_ROOT_DEFAULT

try:
    if uploaded_file is not None:
        df = load_csv(uploaded_file)
        source_name = uploaded_file.name
    elif DEFAULT_CSV.exists():
        df = load_csv(DEFAULT_CSV)
        source_name = DEFAULT_CSV.name
    else:
        st.info("Envie o arquivo CSV na barra lateral para iniciar.")
        st.stop()
except Exception as exc:
    st.error(str(exc))
    st.stop()

with st.sidebar:
    st.caption(f"Arquivo carregado: **{source_name}**")
    st.caption(f"{len(df):,} registros · {len(df.columns)} campos".replace(",", "."))
    st.divider()
    st.header("Filtros")

    search_text = st.text_input(
        "Busca geral",
        placeholder="Tombo, objeto, povo, aldeia, descrição...",
    ).strip()

    #status_selected = st.multiselect(
    #    "Status do cruzamento",
    #    unique_values(df, "status_cruzamento"),
    #)
    collection_selected = st.multiselect(
        "Coleção",
        unique_values(df, "catalogo_nome_da_coleção"),
    )
    people_selected = st.multiselect(
        "Povo",
        unique_values(df, "catalogo_povo"),
    )
    function_selected = st.multiselect(
        "Função",
        unique_values(df, "catalogo_função"),
    )
    format_selected = st.multiselect(
        "Formato do arquivo",
        unique_values(df, "formato"),
    )

filtered = df.copy()
#filtered = apply_multiselect_filter(filtered, "status_cruzamento", status_selected)
filtered = apply_multiselect_filter(filtered, "catalogo_nome_da_coleção", collection_selected)
filtered = apply_multiselect_filter(filtered, "catalogo_povo", people_selected)
filtered = apply_multiselect_filter(filtered, "catalogo_função", function_selected)
filtered = apply_multiselect_filter(filtered, "formato", format_selected)

if search_text:
    searchable_columns = existing_columns(
        filtered,
        [
            "chave_cruzamento", "nome_arquivo", "codigo_acervo",
            "catalogo_número_de_tombo", "catalogo_identificação_museológica",
            "catalogo_nome_da_coleção", "catalogo_descrição", "descricao",
            "palavras_chave", "catalogo_identificação_local", "catalogo_povo",
            "catalogo_auto_denominação", "catalogo_aldeia", "catalogo_autor_artesão",
            "catalogo_material_suporte", "catalogo_técnica", "catalogo_notas_gerais",
        ],
    )
    if searchable_columns:
        mask = pd.Series(False, index=filtered.index)
        for column in searchable_columns:
            mask |= filtered[column].fillna("").astype(str).str.contains(
                search_text, case=False, regex=False
            )
        filtered = filtered[mask]

# Métricas
m1, m2, m3, m4 = st.columns(4)
m1.metric("Registros exibidos", f"{len(filtered):,}".replace(",", "."))
m2.metric(
    "Objetos museológicos",
    f"{filtered.get('catalogo_número_de_tombo', pd.Series(dtype=object)).nunique(dropna=True):,}".replace(",", "."),
)
m3.metric(
    "Coleções",
    f"{filtered.get('catalogo_nome_da_coleção', pd.Series(dtype=object)).nunique(dropna=True):,}".replace(",", "."),
)
m4.metric(
    "Volume das imagens",
    format_size_mb(filtered.get("tamanho_mb", pd.Series(dtype=float)).sum(min_count=1)),
)

if filtered.empty:
    st.warning("Nenhum registro atende aos filtros selecionados.")
    st.stop()

summary_tab, catalog_tab, detail_tab, data_tab = st.tabs(
    ["Visão geral", "Catálogo", "Ficha detalhada", "Dados completos"]
)

with summary_tab:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Registros por coleção")
        if "catalogo_nome_da_coleção" in filtered.columns:
            chart = (
                filtered["catalogo_nome_da_coleção"]
                .fillna("Não informado")
                .value_counts()
                .head(15)
                .rename_axis("Coleção")
                .to_frame("Quantidade")
            )
            st.bar_chart(chart)
    with c2:
        st.subheader("Registros por povo")
        if "catalogo_povo" in filtered.columns:
            chart = (
                filtered["catalogo_povo"]
                .fillna("Não informado")
                .value_counts()
                .head(15)
                .rename_axis("Povo")
                .to_frame("Quantidade")
            )
            st.bar_chart(chart)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Função dos objetos")
        if "catalogo_função" in filtered.columns:
            function_series = (
                filtered["catalogo_função"]
                .fillna("Não informado")
                .astype(str)
                .str.split(r"\s*\|\|\s*")
                .explode()
                .str.strip()
            )
            st.dataframe(
                function_series.value_counts().rename_axis("Função").to_frame("Quantidade"),
                use_container_width=True,
                height=300,
            )
    with c4:
        st.subheader("Equipamentos fotográficos")
        camera_cols = existing_columns(filtered, ["fabricante_camera", "modelo_camera"])
        if camera_cols:
            cameras = filtered[camera_cols].fillna("Não informado").value_counts().reset_index(name="Quantidade")
            st.dataframe(cameras, use_container_width=True, hide_index=True, height=300)

with catalog_tab:
    st.subheader("Catálogo resumido")
    catalog_columns = existing_columns(
        filtered,
        [
            "nome_arquivo", "catalogo_número_de_tombo", "catalogo_identificação_museológica",
            "catalogo_identificação_local", "catalogo_nome_da_coleção", "catalogo_povo",
            "catalogo_aldeia", "catalogo_autor_artesão", "catalogo_material_suporte",
            "catalogo_técnica", "catalogo_função", "catalogo_dimensões",
            "catalogo_estado_de_conservação"
        ],
    )
    st.dataframe(
        filtered[catalog_columns],
        use_container_width=True,
        hide_index=True,
        height=560,
        column_config={
            "nome_arquivo": "Arquivo",
            "catalogo_número_de_tombo": "Número de tombo",
            "catalogo_identificação_museológica": "Identificação museológica",
            "catalogo_identificação_local": "Nome do objeto",
            "catalogo_nome_da_coleção": "Coleção",
            "catalogo_povo": "Povo",
            "catalogo_aldeia": "Aldeia",
            "catalogo_autor_artesão": "Autor/Artesão",
            "catalogo_material_suporte": "Material/Suporte",
            "catalogo_técnica": "Técnica",
            "catalogo_função": "Função",
            "catalogo_dimensões": "Dimensões",
            "catalogo_estado_de_conservação": "Conservação",
            #"status_cruzamento": "Cruzamento",
        },
    )

with detail_tab:
    st.subheader("Ficha individual")
    label_column = "catalogo_número_de_tombo" if "catalogo_número_de_tombo" in filtered.columns else filtered.columns[0]
    options = filtered.index.tolist()

    def record_label(idx: int) -> str:
        row = filtered.loc[idx]
        tombo = text_value(row, label_column, "Sem tombo")
        name = text_value(row, "catalogo_identificação_local", text_value(row, "nome_arquivo", "Sem nome"))
        return f"{tombo} — {name}"

    selected_idx = st.selectbox("Selecione um registro", options, format_func=record_label)
    row = filtered.loc[selected_idx]

    image_col, info_col = st.columns([1, 2])
    with image_col:
        image_path = find_image_path(row, image_root or None)
        if image_path:
            st.image(str(image_path), caption=text_value(row, "nome_arquivo"), use_container_width=True)
        else:
            st.info(
                "Pré-visualização indisponível. Informe na barra lateral a pasta local onde as imagens estão armazenadas."
            )

        st.markdown(
            f"""
            <div class="record-card">
                <div class="small-label">Arquivo</div>
                <div class="big-value">{text_value(row, 'nome_arquivo')}</div>
                <div class="small-label">Dimensão digital</div>
                <div class="big-value">{text_value(row, 'largura_pixels', '—')} × {text_value(row, 'altura_pixels', '—')} px</div>
                <div class="small-label">Tamanho</div>
                <div class="big-value">{format_size_mb(row.get('tamanho_mb'))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with info_col:
        st.markdown(f"### {text_value(row, 'catalogo_identificação_local', 'Objeto sem identificação local')}")
        st.caption(
            f"Tombo: {text_value(row, 'catalogo_número_de_tombo')} · "
            f"Identificação: {text_value(row, 'catalogo_identificação_museológica')}"
        )
        st.write(text_value(row, "catalogo_descrição", text_value(row, "descricao")))

        a, b, c = st.columns(3)
        a.markdown(f"**Coleção**  \n{text_value(row, 'catalogo_nome_da_coleção')}")
        b.markdown(f"**Povo**  \n{text_value(row, 'catalogo_povo')}")
        c.markdown(f"**Aldeia**  \n{text_value(row, 'catalogo_aldeia')}")

        st.divider()
        left, right = st.columns(2)
        with left:
            st.markdown("#### Caracterização")
            st.markdown(f"**Material/Suporte:** {text_value(row, 'catalogo_material_suporte')}")
            st.markdown(f"**Técnica:** {text_value(row, 'catalogo_técnica')}")
            st.markdown(f"**Função:** {text_value(row, 'catalogo_função')}")
            st.markdown(f"**Dimensões:** {text_value(row, 'catalogo_dimensões')}")
            st.markdown(f"**Componentes:** {text_value(row, 'catalogo_quantidade_de_componentes')}")
            st.markdown(f"**Conservação:** {text_value(row, 'catalogo_estado_de_conservação')}")
        with right:
            st.markdown("#### Produção e aquisição")
            st.markdown(f"**Autor/Artesão:** {text_value(row, 'catalogo_autor_artesão')}")
            st.markdown(f"**Data de fabricação:** {text_value(row, 'catalogo_data_de_fabricação')}")
            st.markdown(f"**Cedente:** {text_value(row, 'catalogo_cedente')}")
            st.markdown(f"**Coletor:** {text_value(row, 'catalogo_coletor')}")
            st.markdown(f"**Forma de aquisição:** {text_value(row, 'catalogo_forma_de_aquisição')}")
            st.markdown(f"**Entrada no MN:** {text_value(row, 'catalogo_data_de_entrada_no_mn')}")

        with st.expander("Histórico, documentação e notas"):
            for title, column in [
                ("Histórico administrativo", "catalogo_histórico_administrativo"),
                ("Histórico de exposições", "catalogo_histórico_de_exposições"),
                ("Documentação", "catalogo_documentação"),
                ("Bibliografia", "catalogo_bibliografia"),
                ("Notas gerais", "catalogo_notas_gerais"),
            ]:
                st.markdown(f"**{title}**")
                st.write(text_value(row, column))

        with st.expander("Metadados técnicos da fotografia"):
            tech_columns = existing_columns(
                filtered,
                [
                    "criador_fotografo", "credito", "data_criacao", "software_criacao",
                    "fabricante_camera", "modelo_camera", "lente", "formato", "extensao",
                    "largura_pixels", "altura_pixels", "megapixels", "modo_cor", "resolucao_x",
                    "resolucao_y", "iso", "distancia_focal", "possui_exif", "possui_xmp",
                ],
            )
            tech_df = pd.DataFrame(
                {"Campo": tech_columns, "Valor": [text_value(row, col) for col in tech_columns]}
            )
            st.dataframe(tech_df, use_container_width=True, hide_index=True)

with data_tab:
    st.subheader("Todos os campos")
    display_df = filtered.copy()
    for col in display_df.select_dtypes(include=["datetime64[ns]"]).columns:
        display_df[col] = display_df[col].dt.strftime("%d/%m/%Y %H:%M:%S")
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=580)

    csv_bytes = filtered.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        "Baixar dados filtrados em CSV",
        data=csv_bytes,
        file_name="BaseMN_003_filtrada.csv",
        mime="text/csv",
        use_container_width=False,
    )
