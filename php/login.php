<?php

// Criar conexão
$conn = mysqli_connect("154.56.40.104", "bed", "my_c00L_s3cret", "honeydb", 3306);

if (!$conn) {
    die("Falha na conexão: " . mysqli_connect_error());
}


if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = $conn->real_escape_string($_POST['username']);
    $senha = $_POST['senha']; // senha enviada pelo usuário

    $stmt = $conn->prepare("SELECT senha FROM users WHERE username = ?");
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $result = $stmt->get_result();
    if ($row = $result->fetch_assoc()) {
        if (password_verify($senha, $row['senha'])) {
            header("Location: ../public/logado.html");
            exit();
        } else {
            echo "Senha incorreta!";
        }
    } else {
        echo "Usuário não encontrado!";
    }
    $stmt->close();
}

$conn->close();
?>

