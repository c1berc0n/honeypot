<?php
$host = "154.56.40.104"; // ou o IP do servidor de banco de dados
$username = "bed"; // usuário do banco
$password = "my_c00L_s3cret"; // senha do usuário
$database = "honeybd"; // nome do banco de dados

// Criar conexão
$conn = mysqli_connect($host, $username, $password, $database, 3306);

// Checar conexão
if ($conn->connect_error) {
    die("Falha na conexão: " . $conn->connect_error);
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $nome = $conn->real_escape_string($_POST['nome']);
    $sobrenome = $conn->real_escape_string($_POST['sobrenome']);
    $username = $conn->real_escape_string($_POST['username']);
    $email = $conn->real_escape_string($_POST['email']);
    $senha = password_hash($_POST['senha'], PASSWORD_DEFAULT); // Hash da senha para armazenamento seguro

    $stmt = $conn->prepare("INSERT INTO users (nome, sobrenome, username, email, senha) VALUES (?, ?, ?, ?, ?)");
    $stmt->bind_param("sssss", $nome, $sobrenome, $username, $email, $senha);

    if ($stmt->execute()) {
        echo "Cadastro realizado com sucesso!";
    } else {
        echo "Erro ao cadastrar usuário: " . $stmt->error;
    }

    $stmt->close();
}

$conn->close();
?>
