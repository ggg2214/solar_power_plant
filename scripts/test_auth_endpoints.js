const { handler } = require('../netlify/functions/api-proxy');

async function runTests() {
    console.log("=== Starting Auth & WebAuthn Integration Tests ===");
    let passed = 0;
    let total = 0;

    function assert(condition, message) {
        total++;
        if (condition) {
            console.log(`✅ PASS: ${message}`);
            passed++;
        } else {
            console.error(`❌ FAIL: ${message}`);
        }
    }

    const testEmail = "testuser_solar@example.com";
    const testPassword = "Password123!";

    // 1. Signup
    const signupRes = await handler({
        path: '/.netlify/functions/api-proxy/auth/signup',
        httpMethod: 'POST',
        body: JSON.stringify({ email: testEmail, password: testPassword })
    }, {});
    const signupData = JSON.parse(signupRes.body);
    assert(signupRes.statusCode === 200 && signupData.success === true, "User signup succeeds");

    // 2. Login correct
    const loginRes = await handler({
        path: '/.netlify/functions/api-proxy/auth/login',
        httpMethod: 'POST',
        body: JSON.stringify({ email: testEmail, password: testPassword })
    }, {});
    const loginData = JSON.parse(loginRes.body);
    assert(loginRes.statusCode === 200 && loginData.success === true, "User login with correct credentials succeeds");

    // 3. Login incorrect password
    const loginWrongRes = await handler({
        path: '/.netlify/functions/api-proxy/auth/login',
        httpMethod: 'POST',
        body: JSON.stringify({ email: testEmail, password: 'WrongPassword!' })
    }, {});
    assert(loginWrongRes.statusCode === 401, "User login with wrong credentials rejected");

    // 4. WebAuthn register-options
    const regOptRes = await handler({
        path: '/.netlify/functions/api-proxy/auth/webauthn/register-options',
        httpMethod: 'GET',
        queryStringParameters: { email: testEmail }
    }, {});
    const regOptData = JSON.parse(regOptRes.body);
    assert(regOptRes.statusCode === 200 && typeof regOptData.challenge === 'string', "WebAuthn register-options returns challenge");

    // 5. WebAuthn register-verify
    const testKeyId = "test_passkey_cred_12345";
    const testKeyName = "내 맥북 TouchID";
    const regVerifyRes = await handler({
        path: '/.netlify/functions/api-proxy/auth/webauthn/register-verify',
        httpMethod: 'POST',
        queryStringParameters: { email: testEmail },
        body: JSON.stringify({ id: testKeyId, rawId: testKeyId, name: testKeyName })
    }, {});
    const regVerifyData = JSON.parse(regVerifyRes.body);
    assert(regVerifyRes.statusCode === 200 && regVerifyData.passkeys.some(k => k.id === testKeyId), "WebAuthn register-verify registers passkey");

    // 6. WebAuthn list
    const listRes = await handler({
        path: '/.netlify/functions/api-proxy/auth/webauthn/list',
        httpMethod: 'GET',
        queryStringParameters: { email: testEmail }
    }, {});
    const listData = JSON.parse(listRes.body);
    assert(listRes.statusCode === 200 && listData.passkeys.length > 0 && listData.passkeys[0].name === testKeyName, "WebAuthn list returns saved passkeys");

    // 7. WebAuthn rename
    const newName = "내 회사 노트북 지문";
    const renameRes = await handler({
        path: '/.netlify/functions/api-proxy/auth/webauthn/rename',
        httpMethod: 'POST',
        body: JSON.stringify({ email: testEmail, id: testKeyId, new_name: newName })
    }, {});
    const renameData = JSON.parse(renameRes.body);
    assert(renameRes.statusCode === 200 && renameData.passkeys.some(k => k.id === testKeyId && k.name === newName), "WebAuthn rename updates passkey name");

    // 8. WebAuthn login-options
    const loginOptRes = await handler({
        path: '/.netlify/functions/api-proxy/auth/webauthn/login-options',
        httpMethod: 'GET',
        queryStringParameters: { email: testEmail }
    }, {});
    const loginOptData = JSON.parse(loginOptRes.body);
    assert(loginOptRes.statusCode === 200 && loginOptData.has_passkey === true && loginOptData.allowCredentials.length > 0, "WebAuthn login-options returns allowCredentials");

    // 9. WebAuthn login-verify
    const loginVerifyRes = await handler({
        path: '/.netlify/functions/api-proxy/auth/webauthn/login-verify',
        httpMethod: 'POST',
        queryStringParameters: { email: testEmail },
        body: JSON.stringify({ id: testKeyId })
    }, {});
    assert(loginVerifyRes.statusCode === 200, "WebAuthn login-verify succeeds");

    // 10. WebAuthn delete
    const deleteKeyRes = await handler({
        path: '/.netlify/functions/api-proxy/auth/webauthn/delete',
        httpMethod: 'POST',
        body: JSON.stringify({ email: testEmail, id: testKeyId })
    }, {});
    const deleteKeyData = JSON.parse(deleteKeyRes.body);
    assert(deleteKeyRes.statusCode === 200 && !deleteKeyData.passkeys.some(k => k.id === testKeyId), "WebAuthn delete removes passkey");

    // 11. Delete account
    const deleteAccRes = await handler({
        path: '/.netlify/functions/api-proxy/auth/delete-account',
        httpMethod: 'POST',
        body: JSON.stringify({ email: testEmail })
    }, {});
    assert(deleteAccRes.statusCode === 200, "User account deletion succeeds");

    // 12. Login after delete should fail
    const loginAfterDelete = await handler({
        path: '/.netlify/functions/api-proxy/auth/login',
        httpMethod: 'POST',
        body: JSON.stringify({ email: testEmail, password: testPassword })
    }, {});
    assert(loginAfterDelete.statusCode === 401, "Login after deletion is rejected");

    console.log(`\n=== Test Summary: ${passed}/${total} Passed ===`);
    if (passed === total) {
        process.exit(0);
    } else {
        process.exit(1);
    }
}

runTests().catch(err => {
    console.error("Test runner error:", err);
    process.exit(1);
});
