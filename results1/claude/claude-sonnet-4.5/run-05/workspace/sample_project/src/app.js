// Sample JavaScript with code quality issues

// Warning: var usage
var globalConfig = {
    apiUrl: 'https://api.example.com',
    timeout: 5000
};

function authenticateUser(username, password) {
    // Info: console.log
    console.log('Authenticating user:', username);

    // Warning: loose equality
    if (username == null) {
        return false;
    }

    // TODO: Add proper validation
    // FIXME: This is insecure

    // Critical: eval usage
    var isValid = eval('username.length > 0');

    return isValid;
}

function updateUserProfile(userId, data) {
    // Warning: innerHTML XSS risk
    document.getElementById('profile').innerHTML = data.bio;

    // Info: console.log
    console.log('Profile updated for user', userId);

    // Warning: loose equality
    if (userId == data.id) {
        saveProfile(data);
    }
}

function saveProfile(data) {
    // Warning: document.write
    document.write('<div>Saving...</div>');

    // More console logs
    console.log('Data:', data);
}

// HACK: Temporary workaround for API timeout issue - this line is intentionally made very long to test the line length checker and ensure it properly detects lines that exceed 120 characters

function renderPage() {
    var content = '<h1>Welcome</h1>';
    // Another innerHTML issue
    document.getElementById('app').innerHTML = content;
}
