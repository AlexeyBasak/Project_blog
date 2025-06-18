from django.core.mail.backends.smtp import EmailBackend
import ssl

class CustomEmailBackend(EmailBackend):
    def open(self):
        if self.connection:
            return False
        
        try:
            self.connection = self.connection_class(
                self.host, self.port, **self.connection_kwargs)
            
            if self.use_tls:
                context = ssl.create_default_context()
                if self.ssl_keyfile:
                    context.load_cert_chain(
                        certfile=self.ssl_certfile,
                        keyfile=self.ssl_keyfile
                    )
                self.connection.starttls(context=context)
                
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except Exception:
            if not self.fail_silently:
                raise