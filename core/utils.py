import io
import qrcode
import socket
from pyrad.client import Client
from pyrad.dictionary import Dictionary
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader

def send_radius_coa_disconnect(username, nas_ip, session_id, secret=b"testing123"):
    """
    Envia um pacote RADIUS CoA (Packet of Disconnect) para o NAS/AP.
    """
    # Em um cenário real, o dicionário RADIUS deve estar no sistema
    # Para este exemplo, simularemos a estrutura básica
    try:
        # Configuração do cliente CoA (porta padrão 1700)
        srv = Client(server=nas_ip, secret=secret, dict=Dictionary(io.StringIO("")))
        
        # Criar pacote de desconexão (Code 40: Disconnect-Request)
        req = srv.CreateDisconnectPacket()
        req["User-Name"] = username
        req["Acct-Session-Id"] = session_id
        
        # Enviar (Isso requer que o AP aceite pacotes do IP do servidor Django)
        # srv.SendPacket(req) 
        
        # Simulação para desenvolvimento
        print(f"DEBUG: Enviando CoA Disconnect para {username} no NAS {nas_ip}")
        return True, "Comando enviado com sucesso."
    except Exception as e:
        return False, f"Erro ao enviar CoA: {str(e)}"

def generate_vouchers_pdf(vouchers, base_url="http://127.0.0.1:8000"):
    """
    Gera um PDF em memória contendo cartões de voucher com QR Code.
    Cada página do A4 conterá múltiplos vouchers para economia de papel.
    """
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Configurações do layout (Cartões de 9cm x 6cm)
    card_width = 9 * cm
    card_height = 6 * cm
    margin_x = 1 * cm
    margin_y = 1 * cm
    gap = 0.5 * cm

    x = margin_x
    y = height - margin_y - card_height

    for voucher in vouchers:
        # Desenhar borda do cartão
        p.setStrokeColorRGB(0, 0.17, 0.34) # Cor primária Viposa
        p.setLineWidth(1)
        p.roundRect(x, y, card_width, card_height, 0.2 * cm, stroke=1, fill=0)

        # Cabeçalho do Cartão
        p.setFont("Helvetica-Bold", 12)
        p.drawString(x + 0.5 * cm, y + card_height - 1 * cm, "VIPOSA S.A.")
        p.setFont("Helvetica", 8)
        p.drawString(x + 0.5 * cm, y + card_height - 1.4 * cm, "Acesso Wi-Fi Visitante")

        # Gerar QR Code
        # URL de acesso rápido: http://.../visitante/?code=XXXX
        qr_url = f"{base_url}/visitante/?code={voucher.code}"
        qr = qrcode.QRCode(version=1, box_size=10, border=0)
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Converter imagem PIL para ReportLab
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        qr_img = ImageReader(img_buffer)

        # Posicionar QR Code no cartão
        p.drawImage(qr_img, x + card_width - 2.5 * cm, y + 0.5 * cm, width=2 * cm, height=2 * cm)

        # Texto do Voucher
        p.setFont("Helvetica-Bold", 14)
        p.drawString(x + 0.5 * cm, y + 1.5 * cm, f"CÓDIGO: {voucher.code}")
        
        p.setFont("Helvetica-Oblique", 7)
        p.drawString(x + 0.5 * cm, y + 0.8 * cm, f"Válido até: {voucher.expires_at.strftime('%d/%m/%Y %H:%M')}")
        p.drawString(x + 0.5 * cm, y + 0.4 * cm, "Conecte-se ao Wi-Fi e escaneie o código.")

        # Atualizar coordenadas para o próximo cartão
        x += card_width + gap
        if x + card_width > width - margin_x:
            x = margin_x
            y -= card_height + gap
        
        # Nova página se necessário
        if y < margin_y:
            p.showPage()
            x = margin_x
            y = height - margin_y - card_height

    p.save()
    buffer.seek(0)
    return buffer
