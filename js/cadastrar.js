// Adiciona o evento de entrada no campo de senha
document.addEventListener("DOMContentLoaded", function() {
    var senhaField = document.getElementById('senha');
    if (senhaField) {
        senhaField.addEventListener('input', function() {
            var senha = this.value;
            var forca = 0;
            if (senha.length > 8) forca += 1;
            if (senha.match(/[\d]/)) forca += 1;
            if (senha.match(/[a-z]/)) forca += 1;
            if (senha.match(/[A-Z]/)) forca += 1;
            if (senha.match(/[\W]/)) forca += 1;

            var mensagem = '';
            if (forca < 3) {
                mensagem = 'Senha fraca';
            } else if (forca < 4) {
                mensagem = 'Senha moderada';
            } else {
                mensagem = 'Senha forte';
            }
            alert(mensagem);
        });
    }
});
