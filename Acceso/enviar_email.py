def enviar_correo(error, contenido, asunto):
    import yagmail

    email = 'botgbm@gmail.com'
    contraseña = 'jrxxzqezoihipboz'

    yag = yagmail.SMTP(user=email, password=contraseña)

    destinatario = 'cpsb1201@gmail.com'
    mensaje = f"""
    {contenido}\n
    {error}
    """

    yag.send(destinatario, asunto, mensaje)