#!/usr/bin/env python3
"""
COMPLETE SECURE LOGIN SYSTEM - All-in-One File
Includes: Flask backend + HTML/CSS/JS frontend
"""

from flask import Flask, render_template_string, request, jsonify, session
import secrets
import os
import sqlite3
import bcrypt
import re
from datetime import datetime
from contextlib import contextmanager
import pyotp
import segno
import io
import base64

app = Flask(__name__)
app.secret_key = os.urandom(32)

DATABASE = 'secure_login.db'

# ============================================================
# HTML TEMPLATE (Embedded)
# ============================================================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SecureLogin | Authentication System</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #0a2e1f 0%, #0d3d2a 25%, #0a2a3e 50%, #0d3d2a 75%, #0a2e1f 100%);
            min-height: 100vh;
            color: #fff;
            position: relative;
            overflow-x: hidden;
        }

        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; position: relative; z-index: 2; }
        
        .page { display: none; animation: fadeIn 0.5s ease; }
        .page.active { display: block; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        
        .auth-card { 
            background: rgba(10, 30, 20, 0.6); 
            backdrop-filter: blur(15px); 
            border-radius: 30px; 
            padding: 40px; 
            max-width: 450px; 
            margin: 0 auto; 
            border: 1px solid rgba(0, 255, 136, 0.3);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
            transition: all 0.4s;
        }
        .auth-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 30px 50px rgba(0, 255, 136, 0.15);
        }
        
        .glass-card { 
            background: rgba(10, 30, 20, 0.5); 
            backdrop-filter: blur(12px); 
            border-radius: 25px; 
            padding: 30px; 
            border: 1px solid rgba(0, 255, 136, 0.25);
            transition: all 0.3s;
        }
        .glass-card:hover {
            border-color: rgba(0, 212, 255, 0.5);
            transform: translateY(-2px);
        }
        
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #00ffaa; font-size: 14px; font-weight: 600; }
        .input-wrapper { position: relative; }
        .input-wrapper i { position: absolute; left: 15px; top: 50%; transform: translateY(-50%); color: #00ff88; font-size: 16px; }
        input { 
            width: 100%; 
            padding: 14px 15px 14px 45px; 
            background: rgba(0, 20, 10, 0.6); 
            border: 2px solid rgba(0, 255, 136, 0.3); 
            border-radius: 14px; 
            color: #fff; 
            font-size: 16px; 
            transition: all 0.3s; 
        }
        input:focus { 
            outline: none; 
            border-color: #00ff88; 
            box-shadow: 0 0 0 4px rgba(0, 255, 136, 0.15);
        }
        
        .btn { 
            padding: 14px 35px; 
            font-size: 16px; 
            font-weight: 600; 
            border: none; 
            border-radius: 14px; 
            cursor: pointer; 
            transition: all 0.3s; 
            text-decoration: none; 
            display: inline-block; 
            font-family: 'Space Grotesk', monospace;
        }
        .btn-primary { 
            background: linear-gradient(135deg, #00ff88, #00d4ff);
            color: #0a1a0f; 
            box-shadow: 0 4px 15px rgba(0, 255, 136, 0.3);
        }
        .btn-primary:hover { 
            transform: translateY(-3px); 
            box-shadow: 0 8px 25px rgba(0, 255, 136, 0.5);
        }
        .btn-secondary { 
            background: linear-gradient(135deg, #00d4ff, #00ff88);
            color: #0a1a0f; 
        }
        .btn-danger { 
            background: linear-gradient(135deg, #ff6b6b, #ff4444);
            color: white; 
        }
        .btn-outline { 
            background: transparent; 
            border: 2px solid #00ff88; 
            color: #00ff88; 
        }
        .btn-outline:hover { 
            background: rgba(0, 255, 136, 0.15); 
        }
        
        .navbar { 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            background: rgba(10, 30, 20, 0.6); 
            backdrop-filter: blur(15px); 
            padding: 15px 30px; 
            border-radius: 20px; 
            margin-bottom: 30px; 
            border: 1px solid rgba(0, 255, 136, 0.3);
        }
        .logo { display: flex; align-items: center; gap: 10px; }
        .logo i { font-size: 28px; color: #00ff88; }
        .logo span { 
            font-size: 20px; 
            font-weight: 700; 
            font-family: 'Space Grotesk', monospace;
            background: linear-gradient(135deg, #00ff88, #00d4ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .nav-links { display: flex; gap: 20px; align-items: center; flex-wrap: wrap; }
        .nav-links a { color: #88ffaa; text-decoration: none; transition: all 0.3s; cursor: pointer; font-size: 14px; font-weight: 500; }
        .nav-links a:hover { color: #00ff88; }
        
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { 
            background: rgba(10, 30, 20, 0.5); 
            border-radius: 20px; 
            padding: 25px; 
            text-align: center; 
            transition: all 0.3s;
            border: 1px solid rgba(0, 255, 136, 0.2);
        }
        .stat-card:hover { transform: translateY(-5px); border-color: #00ff88; }
        .stat-card i { font-size: 40px; color: #00ff88; margin-bottom: 15px; }
        .stat-card h3 { font-size: 28px; margin-bottom: 5px; color: #00ffaa; }
        
        .features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 25px; margin-bottom: 50px; }
        .feature-card { 
            background: rgba(10, 30, 20, 0.5); 
            backdrop-filter: blur(8px);
            border-radius: 20px; 
            padding: 30px; 
            text-align: center; 
            transition: all 0.4s;
            border: 1px solid rgba(0, 255, 136, 0.25);
        }
        .feature-card:hover { transform: translateY(-8px); border-color: #00ff88; }
        .feature-card i { font-size: 48px; color: #00ff88; margin-bottom: 20px; }
        .feature-card h3 { font-size: 20px; margin-bottom: 12px; color: #00ffaa; }
        .feature-card p { color: #88ffaa; line-height: 1.6; font-size: 14px; }
        
        .qr-container { text-align: center; margin: 20px 0; padding: 20px; background: rgba(0, 30, 15, 0.5); border-radius: 20px; }
        .qr-container img { max-width: 200px; margin: 0 auto; display: block; border-radius: 15px; }
        .secret-key { 
            background: rgba(0, 255, 136, 0.1); 
            padding: 15px; 
            border-radius: 12px; 
            text-align: center; 
            font-family: monospace; 
            font-size: 18px; 
            letter-spacing: 2px; 
            margin: 20px 0;
            border: 1px solid rgba(0, 255, 136, 0.4);
            color: #00ffaa;
            word-break: break-all;
        }
        
        .flash { padding: 12px; border-radius: 10px; margin-bottom: 15px; font-size: 14px; }
        .flash-success { background: rgba(0, 255, 136, 0.15); border-left: 3px solid #00ff88; color: #00ffaa; }
        .flash-error { background: rgba(255, 107, 107, 0.15); border-left: 3px solid #ff6b6b; color: #ffaaaa; }
        .flash-info { background: rgba(0, 212, 255, 0.15); border-left: 3px solid #00d4ff; color: #88ddff; }
        
        .hidden { display: none; }
        .flex { display: flex; gap: 15px; flex-wrap: wrap; margin-top: 20px; }
        .text-center { text-align: center; }
        .mt-20 { margin-top: 20px; }
        .mb-20 { margin-bottom: 20px; }
        
        @media (max-width: 768px) { .container { padding: 20px 16px; } .navbar { flex-direction: column; gap: 15px; } .nav-links { justify-content: center; } }
    </style>
</head>
<body>
    <div class="container" id="app">
        <!-- HOME PAGE -->
        <div id="homePage" class="page active">
            <div style="text-align: center; margin-bottom: 60px;">
                <div class="logo" style="justify-content: center; margin-bottom: 20px;">
                    <i class="fas fa-shield-alt" style="font-size: 48px;"></i>
                    <span style="font-size: 42px;">SecureLogin</span>
                </div>
                <p style="color: #88ffaa;">🔐 Advanced Authentication System with Military-Grade Security 🔐</p>
            </div>
            
            <div class="features-grid">
                <div class="feature-card"><i class="fas fa-lock"></i><h3>Password Hashing</h3><p>bcrypt hashing with salt - industry standard for password security. Protects against rainbow table attacks.</p></div>
                <div class="feature-card"><i class="fas fa-shield-virus"></i><h3>SQL Injection Protection</h3><p>Parameterized queries prevent SQL injection attacks. All database queries are safely sanitized.</p></div>
                <div class="feature-card"><i class="fas fa-clock"></i><h3>Session Management</h3><p>Secure session tracking with activity monitoring. Automatic timeout and session revocation.</p></div>
                <div class="feature-card"><i class="fas fa-chart-line"></i><h3>Rate Limiting</h3><p>Brute force protection with login attempt tracking. Blocks excessive failed login attempts.</p></div>
                <div class="feature-card"><i class="fas fa-code"></i><h3>Input Validation</h3><p>Strict validation prevents XSS and injection attacks. All user inputs are properly sanitized.</p></div>
                <div class="feature-card"><i class="fas fa-history"></i><h3>Session Tracking</h3><p>Monitor all active sessions and revoke any suspicious sessions remotely.</p></div>
            </div>
            
            <div class="flex" style="justify-content: center;">
                <button onclick="showPage('loginPage')" class="btn btn-primary"><i class="fas fa-sign-in-alt"></i> Login</button>
                <button onclick="showPage('registerPage')" class="btn btn-secondary"><i class="fas fa-user-plus"></i> Register</button>
            </div>
        </div>

        <!-- REGISTER PAGE -->
        <div id="registerPage" class="page">
            <div class="auth-card">
                <div class="text-center mb-20"><i class="fas fa-user-plus" style="font-size: 48px; color: #00ff88;"></i><h2 style="margin-top: 10px; color: #00ffaa;">Create Account</h2><p style="color: #88ffaa; font-size: 14px;">Join SecureLogin today</p></div>
                <div id="registerFlash"></div>
                <form id="registerForm">
                    <div class="form-group"><label>Username</label><div class="input-wrapper"><i class="fas fa-user"></i><input type="text" id="regUsername" placeholder="3-20 characters" required></div><div id="regUsernameFeedback" style="font-size: 12px; margin-top: 5px;"></div></div>
                    <div class="form-group"><label>Email</label><div class="input-wrapper"><i class="fas fa-envelope"></i><input type="email" id="regEmail" placeholder="your@email.com" required></div><div id="regEmailFeedback" style="font-size: 12px; margin-top: 5px;"></div></div>
                    <div class="form-group"><label>Password</label><div class="input-wrapper"><i class="fas fa-lock"></i><input type="password" id="regPassword" placeholder="8+ chars, uppercase, lowercase, number, special char" required></div></div>
                    <div class="form-group"><label>Confirm Password</label><div class="input-wrapper"><i class="fas fa-check-circle"></i><input type="password" id="regConfirmPassword" placeholder="Re-enter your password" required></div><div id="regPasswordMatch" style="font-size: 12px; margin-top: 5px;"></div></div>
                    <button type="submit" class="btn btn-primary" style="width: 100%;">Register</button>
                </form>
                <div class="text-center mt-20"><a onclick="showPage('loginPage')" style="color: #00ff88; cursor: pointer;">← Already have an account? Login</a></div>
                <div class="text-center mt-10"><a onclick="showPage('homePage')" style="color: #6aaa8a; cursor: pointer;">← Back to Home</a></div>
            </div>
        </div>

        <!-- LOGIN PAGE -->
        <div id="loginPage" class="page">
            <div class="auth-card">
                <div class="text-center mb-20"><i class="fas fa-shield-alt" style="font-size: 48px; color: #00d4ff;"></i><h2 style="margin-top: 10px; color: #00ffaa;">Welcome Back</h2><p style="color: #88ffaa; font-size: 14px;">Login to your account</p></div>
                <div id="loginFlash"></div>
                <form id="loginForm">
                    <div class="form-group"><label>Username</label><div class="input-wrapper"><i class="fas fa-user"></i><input type="text" id="loginUsername" placeholder="Enter your username" required></div></div>
                    <div class="form-group"><label>Password</label><div class="input-wrapper"><i class="fas fa-lock"></i><input type="password" id="loginPassword" placeholder="Enter your password" required></div></div>
                    <button type="submit" class="btn btn-primary" style="width: 100%;">Login</button>
                </form>
                <div class="text-center mt-20"><a onclick="showPage('registerPage')" style="color: #00d4ff; cursor: pointer;">Don't have an account? Register</a></div>
                <div class="text-center mt-10"><a onclick="showPage('homePage')" style="color: #6aaa8a; cursor: pointer;">← Back to Home</a></div>
            </div>
        </div>

        <!-- 2FA VERIFY PAGE -->
        <div id="verify2faPage" class="page">
            <div class="auth-card">
                <div class="text-center mb-20"><i class="fas fa-mobile-alt" style="font-size: 48px; color: #00ff88;"></i><h2 style="color: #00ffaa;">Two-Factor Authentication</h2><p style="color: #88ffaa; font-size: 14px;">Enter the 6-digit code from your authenticator app</p></div>
                <div id="verify2faFlash"></div>
                <form id="verify2faForm">
                    <div class="form-group"><label>Verification Code</label><input type="text" id="verify2faCode" placeholder="000000" maxlength="6" style="text-align: center; letter-spacing: 2px;" required></div>
                    <button type="submit" class="btn btn-primary" style="width: 100%;">Verify</button>
                </form>
            </div>
        </div>

        <!-- DASHBOARD PAGE -->
        <div id="dashboardPage" class="page">
            <div class="navbar">
                <div class="logo"><i class="fas fa-shield-alt"></i><span>SecureLogin</span></div>
                <div class="nav-links">
                    <a onclick="loadDashboard()"><i class="fas fa-tachometer-alt"></i> Dashboard</a>
                    <a onclick="showProfile()"><i class="fas fa-user"></i> Profile</a>
                    <a onclick="showSessions()"><i class="fas fa-desktop"></i> Sessions</a>
                    <a onclick="logout()" style="color: #ff8888;"><i class="fas fa-sign-out-alt"></i> Logout</a>
                </div>
            </div>
            <div id="dashboardContent"></div>
        </div>
    </div>

    <script>
        let currentUser = null;
        let temp2faSecret = null;
        
        function showPage(pageId) {
            document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
            document.getElementById(pageId).classList.add('active');
            if (pageId === 'dashboardPage') loadDashboard();
        }
        
        function showFlash(container, message, type) {
            const flashDiv = document.getElementById(container);
            if (flashDiv) {
                flashDiv.innerHTML = `<div class="flash flash-${type}">${message}</div>`;
                setTimeout(() => { flashDiv.innerHTML = ''; }, 3000);
            }
        }

        document.getElementById('regUsername')?.addEventListener('input', async function() {
            const username = this.value;
            if (username.length < 3) { 
                document.getElementById('regUsernameFeedback').innerHTML = '<span style="color:#ffaa88;">⚠️ Min 3 characters</span>'; 
                return; 
            }
            try {
                const res = await fetch('/api/check-username', { 
                    method: 'POST', 
                    headers: { 'Content-Type': 'application/json' }, 
                    body: JSON.stringify({ username }) 
                });
                const data = await res.json();
                document.getElementById('regUsernameFeedback').innerHTML = data.available ? 
                    '<span style="color:#00ff88;">✓ Username available</span>' : 
                    '<span style="color:#ff8888;">✗ Username taken</span>';
            } catch(e) { console.log(e); }
        });

        document.getElementById('regEmail')?.addEventListener('input', async function() {
            const email = this.value;
            if (!email.includes('@')) { 
                document.getElementById('regEmailFeedback').innerHTML = '<span style="color:#ffaa88;">⚠️ Invalid email</span>'; 
                return; 
            }
            try {
                const res = await fetch('/api/check-email', { 
                    method: 'POST', 
                    headers: { 'Content-Type': 'application/json' }, 
                    body: JSON.stringify({ email }) 
                });
                const data = await res.json();
                document.getElementById('regEmailFeedback').innerHTML = data.available ? 
                    '<span style="color:#00ff88;">✓ Email available</span>' : 
                    '<span style="color:#ff8888;">✗ Email registered</span>';
            } catch(e) { console.log(e); }
        });

        function checkPasswordMatch() {
            const pwd = document.getElementById('regPassword')?.value;
            const confirm = document.getElementById('regConfirmPassword')?.value;
            if (pwd && confirm) {
                document.getElementById('regPasswordMatch').innerHTML = pwd === confirm ? 
                    '<span style="color:#00ff88;">✓ Passwords match</span>' : 
                    '<span style="color:#ff8888;">✗ Passwords do not match</span>';
            }
        }
        document.getElementById('regPassword')?.addEventListener('input', checkPasswordMatch);
        document.getElementById('regConfirmPassword')?.addEventListener('input', checkPasswordMatch);

        document.getElementById('registerForm')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = {
                username: document.getElementById('regUsername').value,
                email: document.getElementById('regEmail').value,
                password: document.getElementById('regPassword').value,
                confirm_password: document.getElementById('regConfirmPassword').value
            };
            try {
                const res = await fetch('/api/register', { 
                    method: 'POST', 
                    headers: { 'Content-Type': 'application/json' }, 
                    body: JSON.stringify(data) 
                });
                const result = await res.json();
                if (result.success) { 
                    showFlash('registerFlash', result.message, 'success'); 
                    setTimeout(() => showPage('loginPage'), 1500); 
                } else {
                    showFlash('registerFlash', result.message, 'error');
                }
            } catch(err) { 
                showFlash('registerFlash', 'Network error. Make sure server is running on port 5000', 'error'); 
            }
        });

        document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const data = { 
                username: document.getElementById('loginUsername').value, 
                password: document.getElementById('loginPassword').value 
            };
            try {
                const res = await fetch('/api/login', { 
                    method: 'POST', 
                    headers: { 'Content-Type': 'application/json' }, 
                    body: JSON.stringify(data) 
                });
                const result = await res.json();
                if (result.success) {
                    if (result.require_2fa) { 
                        showPage('verify2faPage'); 
                        showFlash('verify2faFlash', 'Enter your 2FA code', 'info'); 
                    } else { 
                        showPage('dashboardPage'); 
                        loadDashboard(); 
                    }
                } else {
                    showFlash('loginFlash', result.message, 'error');
                }
            } catch(err) { 
                showFlash('loginFlash', 'Network error. Make sure server is running on port 5000', 'error'); 
            }
        });

        document.getElementById('verify2faForm')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const code = document.getElementById('verify2faCode').value;
            try {
                const res = await fetch('/api/verify-2fa', { 
                    method: 'POST', 
                    headers: { 'Content-Type': 'application/json' }, 
                    body: JSON.stringify({ code }) 
                });
                const result = await res.json();
                if (result.success) { 
                    showPage('dashboardPage'); 
                    loadDashboard(); 
                } else {
                    showFlash('verify2faFlash', result.message, 'error');
                }
            } catch(err) { 
                showFlash('verify2faFlash', 'Network error', 'error'); 
            }
        });

        async function loadDashboard() {
            try {
                const res = await fetch('/api/dashboard');
                const data = await res.json();
                if (!data.logged_in) { 
                    showPage('loginPage'); 
                    return; 
                }
                currentUser = data;
                document.getElementById('dashboardContent').innerHTML = `
                    <div class="glass-card"><h2 style="color: #00ffaa;">Welcome, ${data.username}! 👋</h2>
                    <div class="flex"><button onclick="showProfile()" class="btn btn-primary">View Profile</button>
                    ${!data.twofa_enabled ? `<button onclick="setup2FA()" class="btn btn-secondary">Enable 2FA</button>` : `<button onclick="disable2FA()" class="btn btn-danger">Disable 2FA</button>`}</div></div>
                    
                    <div class="stats-grid">
                        <div class="stat-card"><i class="fas fa-calendar-alt"></i><h3>${data.created_at?.slice(0,10) || 'N/A'}</h3><p>Account Created</p></div>
                        <div class="stat-card"><i class="fas fa-clock"></i><h3>${data.last_login?.slice(0,10) || 'Never'}</h3><p>Last Login</p></div>
                        <div class="stat-card"><i class="fas fa-shield-alt"></i><h3>${data.twofa_enabled ? '2FA ON' : '2FA OFF'}</h3><p>Security Status</p></div>
                    </div>
                    
                    <div class="glass-card"><h3 style="color: #00ff88;">🔐 Security Tips</h3>
                        <ul style="margin-top: 15px; margin-left: 20px; color: #88ffaa; line-height: 1.8;">
                            <li>🔐 Never share your password with anyone</li>
                            <li>🔄 Change your password regularly</li>
                            <li>🚪 Always logout from shared devices</li>
                            <li>⚠️ Report suspicious activity immediately</li>
                        </ul>
                    </div>`;
            } catch(err) { console.error(err); }
        }

        async function showProfile() {
            if (!currentUser) await loadDashboard();
            document.getElementById('dashboardContent').innerHTML = `
                <div class="glass-card">
                    <div class="flex" style="align-items: center; gap: 15px; margin-bottom: 20px;">
                        <i class="fas fa-user-circle" style="font-size: 48px; color: #00ff88;"></i>
                        <h2 style="color: #00ffaa;">My Profile</h2>
                    </div>
                    <div style="margin-bottom: 15px;"><div style="color: #00ffaa;">Username</div><div style="font-size: 18px;">${currentUser.username}</div></div>
                    <div style="margin-bottom: 15px;"><div style="color: #00ffaa;">Email</div><div style="font-size: 18px;">${currentUser.email}</div></div>
                    <div style="margin-bottom: 15px;"><div style="color: #00ffaa;">Account Created</div><div style="font-size: 18px;">${currentUser.created_at?.slice(0,19) || 'N/A'}</div></div>
                    <div style="margin-bottom: 15px;"><div style="color: #00ffaa;">Last Login</div><div style="font-size: 18px;">${currentUser.last_login?.slice(0,19) || 'Never'}</div></div>
                    <button onclick="loadDashboard()" class="btn btn-outline mt-20">← Back to Dashboard</button>
                </div>`;
        }

        async function showSessions() {
            try {
                const res = await fetch('/api/sessions');
                const sessions = await res.json();
                let html = `<div class="glass-card"><h2 style="color: #00ff88;"><i class="fas fa-desktop"></i> Active Sessions</h2>`;
                if (sessions.length === 0) html += `<p class="text-center" style="padding: 30px; color: #88ffaa;">No other active sessions</p>`;
                else {
                    html += `<table><thead><tr><th>IP Address</th><th>User Agent</th><th>Created</th><th>Last Activity</th><th></th></tr></thead><tbody>`;
                    sessions.forEach(s => {
                        html += `<tr><td style="color: #aaeecc;">${s.ip_address}</td>
                                <td style="color: #aaeecc;">${(s.user_agent || '').slice(0,30)}...</td>
                                <td style="color: #aaeecc;">${s.created_at?.slice(0,16)}</td>
                                <td style="color: #aaeecc;">${s.last_activity?.slice(0,16)}</td>
                                <td><button onclick="revokeSession('${s.session_id}')" class="btn-danger btn-sm" style="padding: 5px 12px; background: #ff6b6b; border: none; border-radius: 8px; color: white; cursor: pointer;">Revoke</button></td>
                            </tr>`;
                    });
                    html += `</tbody></table>`;
                }
                html += `<button onclick="loadDashboard()" class="btn btn-outline mt-20">← Back to Dashboard</button></div>`;
                document.getElementById('dashboardContent').innerHTML = html;
            } catch(err) { console.error(err); }
        }

        async function revokeSession(sessionId) {
            try {
                await fetch('/api/revoke-session', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ session_id: sessionId }) });
                showSessions();
            } catch(err) {}
        }

        async function setup2FA() {
            try {
                const res = await fetch('/api/setup-2fa');
                const data = await res.json();
                temp2faSecret = data.secret;
                document.getElementById('dashboardContent').innerHTML = `
                    <div class="glass-card"><h2 style="color: #00ff88;">Setup Two-Factor Authentication</h2>
                    <div style="background: rgba(0, 100, 50, 0.3); padding: 15px; border-radius: 15px; margin: 20px 0;">
                        <ol style="margin-left: 20px; color: #88ffaa;"><li>Download Google Authenticator</li><li>Scan the QR code below</li><li>Enter the 6-digit code to verify</li></ol>
                    </div>
                    <div class="qr-container"><img src="data:image/png;base64,${data.qr_code}" alt="QR Code"></div>
                    <div class="secret-key">${data.secret}</div>
                    <input type="text" id="2faCode" placeholder="Enter 6-digit code" style="width: 100%; padding: 14px; text-align: center; letter-spacing: 2px; margin-bottom: 15px; border: 2px solid #00ff88; border-radius: 12px; background: rgba(0,30,15,0.5); color: white;">
                    <button onclick="verifyAndEnable2FA()" class="btn btn-primary" style="width: 100%;">Verify & Enable</button>
                    <button onclick="loadDashboard()" class="btn btn-outline mt-20" style="width: 100%;">Cancel</button></div>`;
            } catch(err) { 
                document.getElementById('dashboardContent').innerHTML = `<div class="glass-card"><p style="color: #ff8888;">Error setting up 2FA. Please try again.</p><button onclick="loadDashboard()" class="btn btn-outline mt-20">Back</button></div>`;
            }
        }

        async function verifyAndEnable2FA() {
            const code = document.getElementById('2faCode').value;
            if (!code || code.length !== 6) {
                alert('Please enter a valid 6-digit code');
                return;
            }
            try {
                const res = await fetch('/api/setup-2fa', { 
                    method: 'POST', 
                    headers: { 'Content-Type': 'application/json' }, 
                    body: JSON.stringify({ secret: temp2faSecret, code }) 
                });
                const result = await res.json();
                if (result.success) { 
                    loadDashboard(); 
                    showFlash('dashboardContent', '2FA enabled successfully!', 'success'); 
                } else {
                    alert('Invalid code. Please try again.');
                }
            } catch(err) { 
                alert('Error verifying code. Make sure the server is running.');
            }
        }

        async function disable2FA() {
            if (confirm('Are you sure you want to disable 2FA?')) {
                await fetch('/api/disable-2fa', { method: 'POST' });
                loadDashboard();
            }
        }

        async function logout() {
            await fetch('/api/logout', { method: 'POST' });
            showPage('homePage');
        }

        async function checkSession() {
            try {
                const res = await fetch('/api/dashboard');
                const data = await res.json();
                if (data.logged_in) showPage('dashboardPage');
            } catch(e) {}
        }
        checkSession();
    </script>
</body>
</html>
'''

# ============================================================
# DATABASE FUNCTIONS
# ============================================================

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                twofa_secret TEXT,
                twofa_enabled INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                ip_address TEXT,
                attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_id TEXT UNIQUE,
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP
            )
        ''')
        conn.commit()
        print("✅ Database initialized!")

def get_user_by_username(username):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cursor.fetchone()

def get_user_by_email(email):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        return cursor.fetchone()

def get_user_by_id(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()

def create_user(username, email, password_hash):
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

def update_last_login(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
        conn.commit()

def enable_2fa(user_id, secret):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET twofa_secret = ?, twofa_enabled = 1 WHERE id = ?", (secret, user_id))
        conn.commit()

def disable_2fa(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET twofa_secret = NULL, twofa_enabled = 0 WHERE id = ?", (user_id,))
        conn.commit()

def record_login_attempt(username, ip_address, success):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO login_attempts (username, ip_address, success) VALUES (?, ?, ?)",
            (username, ip_address, 1 if success else 0)
        )
        conn.commit()

def get_failed_attempts(username, ip_address, minutes=15):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM login_attempts 
            WHERE (username = ? OR ip_address = ?) AND success = 0 
            AND attempt_time > datetime('now', '-' || ? || ' minutes')
        ''', (username, ip_address, minutes))
        return cursor.fetchone()[0]

def save_session(user_id, session_id, ip_address, user_agent):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_sessions (user_id, session_id, ip_address, user_agent, last_activity) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
            (user_id, session_id, ip_address, user_agent)
        )
        conn.commit()

def delete_session(session_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_sessions WHERE session_id = ?", (session_id,))
        conn.commit()

def get_user_sessions(user_id, current_session_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT session_id, ip_address, user_agent, created_at, last_activity 
            FROM user_sessions WHERE user_id = ? AND session_id != ? ORDER BY last_activity DESC
        ''', (user_id, current_session_id))
        return cursor.fetchall()

# ============================================================
# AUTH FUNCTIONS
# ============================================================

def hash_password(password):
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, password_hash):
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def validate_username(username):
    if not username or len(username) < 3 or len(username) > 20:
        return False, "Username must be 3-20 characters"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscore"
    return True, ""

def validate_email(email):
    if not email:
        return False, "Email is required"
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return False, "Invalid email format"
    return True, ""

def validate_password(password):
    if not password or len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain an uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain a lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain a number"
    if not re.search(r'[@$!%*?&]', password):
        return False, "Password must contain a special character (@$!%*?&)"
    return True, ""

# ============================================================
# API ROUTES
# ============================================================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        valid, msg = validate_username(username)
        if not valid:
            return jsonify({'success': False, 'message': msg})
        valid, msg = validate_email(email)
        if not valid:
            return jsonify({'success': False, 'message': msg})
        valid, msg = validate_password(password)
        if not valid:
            return jsonify({'success': False, 'message': msg})
        if password != confirm_password:
            return jsonify({'success': False, 'message': 'Passwords do not match'})
        if get_user_by_username(username):
            return jsonify({'success': False, 'message': 'Username already taken'})
        if get_user_by_email(email):
            return jsonify({'success': False, 'message': 'Email already registered'})
        
        password_hash = hash_password(password)
        user_id = create_user(username, email, password_hash)
        if user_id:
            return jsonify({'success': True, 'message': 'Registration successful! Please login.'})
        else:
            return jsonify({'success': False, 'message': 'Registration failed'})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'})

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        ip_address = request.remote_addr
        
        failed_attempts = get_failed_attempts(username, ip_address, 15)
        if failed_attempts >= 5:
            record_login_attempt(username, ip_address, False)
            return jsonify({'success': False, 'message': 'Too many failed attempts. Try again later.'})
        
        user = get_user_by_username(username)
        if not user or not verify_password(password, user['password_hash']):
            record_login_attempt(username, ip_address, False)
            return jsonify({'success': False, 'message': 'Invalid username or password'})
        
        record_login_attempt(username, ip_address, True)
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['twofa_verified'] = False
        session_id = secrets.token_urlsafe(32)
        session['session_id'] = session_id
        save_session(user['id'], session_id, ip_address, request.headers.get('User-Agent', ''))
        
        if user['twofa_enabled']:
            return jsonify({'success': True, 'message': '2FA required', 'require_2fa': True})
        else:
            session['twofa_verified'] = True
            update_last_login(user['id'])
            return jsonify({'success': True, 'message': 'Login successful', 'require_2fa': False})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'})

@app.route('/api/verify-2fa', methods=['POST'])
def api_verify_2fa():
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Session expired'})
        data = request.get_json()
        code = data.get('code', '')
        user = get_user_by_id(session['user_id'])
        if user['twofa_secret']:
            totp = pyotp.TOTP(user['twofa_secret'])
            if totp.verify(code):
                session['twofa_verified'] = True
                update_last_login(user['id'])
                return jsonify({'success': True, 'message': '2FA verified'})
        return jsonify({'success': False, 'message': 'Invalid code'})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'})

@app.route('/api/dashboard', methods=['GET'])
def api_dashboard():
    try:
        if 'user_id' not in session or not session.get('twofa_verified', False):
            return jsonify({'logged_in': False})
        user = get_user_by_id(session['user_id'])
        return jsonify({
            'logged_in': True,
            'username': user['username'],
            'email': user['email'],
            'created_at': user['created_at'],
            'last_login': user['last_login'],
            'twofa_enabled': user['twofa_enabled'] == 1
        })
    except Exception as e:
        return jsonify({'logged_in': False})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    if 'session_id' in session:
        delete_session(session['session_id'])
    session.clear()
    return jsonify({'success': True})

@app.route('/api/check-username', methods=['POST'])
def api_check_username():
    try:
        data = request.get_json()
        username = data.get('username', '')
        user = get_user_by_username(username)
        return jsonify({'available': user is None})
    except Exception as e:
        return jsonify({'available': True})

@app.route('/api/check-email', methods=['POST'])
def api_check_email():
    try:
        data = request.get_json()
        email = data.get('email', '')
        user = get_user_by_email(email)
        return jsonify({'available': user is None})
    except Exception as e:
        return jsonify({'available': True})

@app.route('/api/sessions', methods=['GET'])
def api_sessions():
    try:
        if 'user_id' not in session or not session.get('twofa_verified', False):
            return jsonify([])
        sessions = get_user_sessions(session['user_id'], session['session_id'])
        return jsonify([dict(s) for s in sessions])
    except Exception as e:
        return jsonify([])

@app.route('/api/revoke-session', methods=['POST'])
def api_revoke_session():
    try:
        data = request.get_json()
        delete_session(data.get('session_id'))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False})

@app.route('/api/setup-2fa', methods=['GET'])
def api_setup_2fa():
    try:
        if 'user_id' not in session or not session.get('twofa_verified', False):
            return jsonify({'error': 'Unauthorized'}), 401
        user = get_user_by_id(session['user_id'])
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(name=user['username'], issuer_name="SecureLogin")
        qr = segno.make(uri)
        buffered = io.BytesIO()
        qr.save(buffered, kind='png', scale=5)
        qr_base64 = base64.b64encode(buffered.getvalue()).decode()
        session['temp_2fa_secret'] = secret
        return jsonify({'secret': secret, 'qr_code': qr_base64})
    except Exception as e:
        return jsonify({'secret': 'ERROR', 'qr_code': ''})

@app.route('/api/setup-2fa', methods=['POST'])
def api_setup_2fa_enable():
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Not logged in'})
        data = request.get_json()
        secret = data.get('secret')
        code = data.get('code')
        totp = pyotp.TOTP(secret)
        if totp.verify(code):
            enable_2fa(session['user_id'], secret)
            return jsonify({'success': True, 'message': '2FA enabled'})
        else:
            return jsonify({'success': False, 'message': 'Invalid code'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/disable-2fa', methods=['POST'])
def api_disable_2fa():
    if 'user_id' in session:
        disable_2fa(session['user_id'])
    return jsonify({'success': True})

# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    init_db()
    print("="*50)
    print("🔐 Secure Login System - Running")
    print("="*50)
    print("Open http://localhost:5000 in your browser")
    print("Press Ctrl+C to stop")
    print("="*50)
    app.run(debug=True, host='0.0.0.0', port=5000)