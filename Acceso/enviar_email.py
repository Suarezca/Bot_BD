def enviar_correo(contenido, asunto):
    import yagmail

    email = 'botgbm@gmail.com'
    contraseña = 'jrxxzqezoihipboz'

    yag = yagmail.SMTP(user=email, password=contraseña)

    destinatario = 'cpsb1201@gmail.com'
    mensaje = f"""
    {contenido}
    """

    yag.send(destinatario, asunto, mensaje)