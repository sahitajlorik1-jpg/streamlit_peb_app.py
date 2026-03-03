import streamlit as st
import anthropic
import base64
import json
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Configuration de la page
st.set_page_config(
    page_title="RenovateWise - Analyse PEB",
    page_icon="🏠",
    layout="wide"
)

# CSS personnalisé
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #D4AF37;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
    .subtitle {
        text-align: center;
        color: #2E75B6;
        font-size: 1.5em;
        margin-bottom: 2em;
    }
    .stButton>button {
        background-color: #D4AF37;
        color: white;
        font-weight: bold;
        padding: 0.5em 2em;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #B8941F;
    }
    </style>
""", unsafe_allow_html=True)

# Récupération de la clé API depuis Streamlit Secrets
try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    st.error("❌ Erreur de configuration. Contactez l'administrateur.")
    st.stop()

# Fonction pour générer le PDF
def generer_pdf_rapport(rapport_data):
    """Génère un PDF professionnel à partir des données du rapport"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Style titre principal
    style_titre = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#D4AF37'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Style sous-titre
    style_soustitre = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor('#2E75B6'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Style heading 1
    style_h1 = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#D4AF37'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    # Style heading 2
    style_h2 = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2E75B6'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    # Style texte normal
    style_normal = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        fontName='Helvetica'
    )
    
    # Style bullet
    style_bullet = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontSize=11,
        leftIndent=20,
        spaceAfter=6,
        fontName='Helvetica'
    )
    
    # Construction du document
    story = []
    
    # PAGE DE GARDE
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("RAPPORT D'ANALYSE PEB", style_titre))
    story.append(Paragraph("Performance Énergétique & Recommandations", style_soustitre))
    
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph(f"<b>{rapport_data['bien']['adresse']}</b>", 
                          ParagraphStyle('addr', parent=style_normal, fontSize=14, alignment=TA_CENTER)))
    
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"Certificat PEB N° {rapport_data['bien']['numero_peb']}", 
                          ParagraphStyle('peb', parent=style_normal, fontSize=12, alignment=TA_CENTER)))
    story.append(Paragraph(f"Superficie : {rapport_data['bien']['superficie_peb']} m²", 
                          ParagraphStyle('surf', parent=style_normal, fontSize=12, alignment=TA_CENTER)))
    
    story.append(PageBreak())
    
    # 1. SYNTHÈSE DE LA PERFORMANCE ACTUELLE
    story.append(Paragraph("1. SYNTHÈSE DE LA PERFORMANCE ACTUELLE", style_h1))
    
    # Tableau synthèse
    data_synthese = [
        ['INDICATEUR', 'VALEUR'],
        ['Classe énergétique', f"{rapport_data['bien']['score_lettre']} ({rapport_data['bien']['score_valeur']} kWh/m².an)"],
        ['Objectif PEB 275 (2033)', '❌ NON ATTEINT (actuellement)'],
        ['Objectif PEB 150 (2045)', '❌ NON ATTEINT (actuellement)']
    ]
    
    table_synthese = Table(data_synthese, colWidths=[8*cm, 8*cm])
    table_synthese.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E75B6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
    ]))
    
    story.append(table_synthese)
    story.append(Spacer(1, 0.5*cm))
    
    # 2. PLAN D'ACTION RECOMMANDÉ
    story.append(Paragraph("2. PLAN D'ACTION RECOMMANDÉ", style_h1))
    story.append(Paragraph("Votre bien nécessite une approche par étapes pour atteindre les objectifs PEB.", style_normal))
    story.append(Spacer(1, 0.3*cm))
    
    # Pour chaque étape
    for etape in rapport_data['scenario_renovation']:
        story.append(Paragraph(f"ÉTAPE {etape['etape']} : {etape['action'].upper()}", style_h2))
        
        # Type de travaux avec couleur
        type_color = '#228B22' if etape['type_travaux'] == 'Privatif' else '#CC5500'
        story.append(Paragraph(f"<font color='{type_color}'><b>Type : {etape['type_travaux']}</b></font>", style_normal))
        
        # Description
        story.append(Paragraph(etape['description'], style_normal))
        
        # Tableau performance
        data_perf = [
            ['Score avant', 'Score après', 'Gain énergétique'],
            [
                f"{etape['score_avant']} kWh/m².an",
                f"{etape['classe_apres']} - {etape['score_apres']} kWh/m².an",
                f"-{etape['gain_kwh']} kWh/m².an (-{etape['gain_pourcentage']}%)"
            ]
        ]
        
        table_perf = Table(data_perf, colWidths=[5*cm, 6*cm, 5*cm])
        table_perf.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D5E8F0')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
            ('BACKGROUND', (2, 1), (2, 1), colors.HexColor('#E5F5E5'))
        ]))
        
        story.append(Spacer(1, 0.2*cm))
        story.append(table_perf)
        story.append(Spacer(1, 0.5*cm))
    
    # 3. SYNTHÈSE GLOBALE
    story.append(Paragraph("3. SYNTHÈSE GLOBALE DES GAINS", style_h1))
    
    synthese = rapport_data['synthese_globale']
    
    # Tableau synthèse globale
    data_globale = [
        ['Aspect', 'Valeur'],
        ['Réduction totale', f"-{synthese['reduction_totale_kwh']} kWh/m².an (-{synthese['reduction_totale_pourcentage']}%)"],
        ['Objectif PEB 275 (2033)', '✅ ATTEINT' if synthese['objectif_2033_atteint_apres'] else '❌ NON ATTEINT'],
        ['Objectif PEB 150 (2045)', '✅ ATTEINT' if synthese['objectif_2045_atteint_apres'] else '❌ NON ATTEINT']
    ]
    
    table_globale = Table(data_globale, colWidths=[8*cm, 8*cm])
    table_globale.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E75B6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
    ]))
    
    story.append(table_globale)
    story.append(Spacer(1, 0.5*cm))
    
    # Message de félicitations si objectifs atteints
    if synthese['objectif_2033_atteint_apres'] and synthese['objectif_2045_atteint_apres']:
        story.append(Paragraph("<font color='#228B22'><b>🎯 FÉLICITATIONS !</b></font>", 
                              ParagraphStyle('felicitations', parent=style_normal, fontSize=14, alignment=TA_CENTER)))
        story.append(Paragraph("En suivant ce plan d'action complet, votre bien atteindra les deux objectifs réglementaires.", 
                              style_normal))
    
    story.append(Spacer(1, 0.5*cm))
    
    # 4. RECOMMANDATIONS
    story.append(Paragraph("4. RECOMMANDATIONS", style_h1))
    
    for i, reco in enumerate(rapport_data['recommandations'], 1):
        story.append(Paragraph(f"• {reco}", style_bullet))
    
    # Footer
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("_" * 80, 
                          ParagraphStyle('line', parent=style_normal, fontSize=8, alignment=TA_CENTER)))
    story.append(Paragraph("<i>Ce rapport a été généré automatiquement à partir de votre certificat PEB</i>", 
                          ParagraphStyle('footer', parent=style_normal, fontSize=9, alignment=TA_CENTER, textColor=colors.grey)))
    story.append(Paragraph("<font color='#2E75B6'>RenovateWise - Analyse intelligente de performance énergétique</font>", 
                          ParagraphStyle('footer2', parent=style_normal, fontSize=9, alignment=TA_CENTER)))
    
    # Génération du PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

# Titre
st.markdown('<h1 class="main-title">🏠 RenovateWise</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Analyse intelligente de votre certificat PEB</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📋 Instructions")
    st.markdown("""
    1. Uploadez votre certificat PEB (PDF)
    2. Cliquez sur "Analyser"
    3. Téléchargez votre rapport PDF
    """)
    
    st.divider()
    st.markdown("### ℹ️ À propos")
    st.markdown("""
    RenovateWise analyse automatiquement votre certificat PEB 
    et génère un plan d'action personnalisé pour améliorer 
    la performance énergétique de votre bien.
    """)

# Zone principale
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Upload du fichier
    uploaded_file = st.file_uploader(
        "📄 Uploadez votre certificat PEB",
        type=['pdf'],
        help="Format accepté : PDF uniquement"
    )
    
    if uploaded_file:
        st.success(f"✅ Fichier chargé : {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
        
        # Bouton d'analyse
        if st.button("🚀 Analyser mon certificat PEB", use_container_width=True):
            
            # Barre de progression
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Étape 1 : Lecture du PDF
                status_text.text("📖 Lecture du certificat PEB...")
                progress_bar.progress(10)
                
                pdf_bytes = uploaded_file.read()
                pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
                
                # Étape 2 : Analyse avec Claude
                status_text.text("🤖 Analyse intelligente en cours...")
                progress_bar.progress(30)
                
                client = anthropic.Anthropic(api_key=api_key)
                
                SYSTEM_PROMPT = """Tu es un expert en performance énergétique des bâtiments en Belgique, spécialisé dans l'analyse des certificats PEB.

Ta mission est d'analyser un certificat PEB et de générer un rapport complet au format JSON structuré.

RÈGLES IMPORTANTES :
- Extrais TOUTES les données avec précision
- Calcule le gain énergétique exact à chaque étape
- Vérifie si le bien est en copropriété
- Pour les objectifs : score ≤ 275 ATTEINT l'objectif 2033, score ≤ 150 ATTEINT l'objectif 2045
- Sois précis sur les surfaces, valeurs U, économies

Réponds UNIQUEMENT avec un objet JSON valide."""

                USER_PROMPT = """Analyse ce certificat PEB et génère un rapport au format JSON avec :
- bien (adresse, superficie, score actuel, etc.)
- scenario_renovation (chaque étape avec gains calculés)
- synthese_globale (réduction totale)
- recommandations pratiques

Structure JSON attendue :
{
  "bien": {
    "adresse": "string",
    "numero_peb": "string",
    "superficie_peb": number,
    "score_valeur": number,
    "score_lettre": "string"
  },
  "scenario_renovation": [
    {
      "etape": number,
      "action": "string",
      "description": "string",
      "type_travaux": "Commun ou Privatif",
      "score_avant": number,
      "score_apres": number,
      "classe_apres": "string",
      "gain_kwh": number,
      "gain_pourcentage": number
    }
  ],
  "synthese_globale": {
    "reduction_totale_kwh": number,
    "reduction_totale_pourcentage": number,
    "objectif_2033_atteint_apres": boolean,
    "objectif_2045_atteint_apres": boolean
  },
  "recommandations": ["array de strings"]
}

Réponds UNIQUEMENT avec le JSON."""

                message = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4000,
                    system=SYSTEM_PROMPT,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "document",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "application/pdf",
                                        "data": pdf_base64
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": USER_PROMPT
                                }
                            ]
                        }
                    ]
                )
                
                progress_bar.progress(60)
                status_text.text("📊 Extraction des données...")
                
                # Extraction du JSON
                json_text = message.content[0].text
                # Nettoyage si besoin
                json_text = json_text[json_text.find('{'):json_text.rfind('}')+1]
                rapport_data = json.loads(json_text)
                
                # Étape 3 : Génération du rapport PDF
                status_text.text("📝 Génération du rapport PDF...")
                progress_bar.progress(80)
                
                pdf_buffer = generer_pdf_rapport(rapport_data)
                
                progress_bar.progress(100)
                status_text.text("✅ Analyse terminée !")
                
                # Affichage des résultats
                st.success("🎉 Rapport généré avec succès !")
                
                # Bouton de téléchargement
                st.download_button(
                    label="📥 Télécharger le rapport (PDF)",
                    data=pdf_buffer,
                    file_name=f"Rapport_PEB_{rapport_data['bien']['numero_peb']}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
                # Aperçu des données
                with st.expander("👁️ Aperçu des données extraites"):
                    st.json(rapport_data)
                
            except json.JSONDecodeError as e:
                st.error(f"❌ Erreur de parsing JSON : {str(e)}")
                st.code(json_text)
            except anthropic.APIError as e:
                st.error(f"❌ Erreur API Claude : {str(e)}")
            except Exception as e:
                st.error(f"❌ Erreur : {str(e)}")
                import traceback
                st.code(traceback.format_exc())

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: #666; padding: 2em;'>
        <p>🏠 <strong>RenovateWise</strong> - Analyse intelligente de performance énergétique</p>
        <p style='font-size: 0.9em;'>Propulsé par Claude AI | © 2025</p>
    </div>
""", unsafe_allow_html=True)
