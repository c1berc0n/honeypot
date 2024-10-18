<?php

// Criar conexão
$conn = mysqli_connect("154.56.40.104", "bed", "my_c00L_s3cret", "honeydb", 3306);

if (!$conn) {
    die("Falha na conexão: " . mysqli_connect_error());
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $nome = $conn->real_escape_string($_POST['nome']);
    $sobrenome = $conn->real_escape_string($_POST['sobrenome']);
    $username = $conn->real_escape_string($_POST['username']);
    $email = $conn->real_escape_string($_POST['email']);
    $senha = password_hash($_POST['senha'], PASSWORD_DEFAULT); // Hash da senha para armazenamento seguro

    $stmt = $conn->prepare("INSERT INTO users (nome, sobrenome, username, email, senha) VALUES (?, ?, ?, ?, ?)");
    if (!$stmt) {
        die("Erro na preparação: " . $conn->error);
    }
    $stmt->bind_param("sssss", $nome, $sobrenome, $username, $email, $senha);
    if (!$stmt->execute()) {
        echo "Erro ao cadastrar usuário: " . $stmt->error;
    } else {
        header("Location: ../public/metricas.html");
        exit();
    }
    $stmt->close();
    
}

$conn->close();
?>
