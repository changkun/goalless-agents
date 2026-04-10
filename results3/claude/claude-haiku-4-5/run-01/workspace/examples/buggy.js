// Example file with some code issues for review
function processUserData(data) {
  let result = [];
  for (let i = 0; i < data.length; i++) {
    if (data[i].age > 18) {
      result.push(data[i]);
    }
  }
  return result;
}

// Calculates fibonacci
function fib(n) {
  if (n <= 1) return n;
  return fib(n - 1) + fib(n - 2);
}

// Global state - not ideal
let cache = {};

function memoizedFib(n) {
  if (cache[n] !== undefined) {
    return cache[n];
  }
  const result = fib(n);
  cache[n] = result;
  return result;
}

// API call without error handling
async function fetchUser(id) {
  const response = await fetch(`/api/users/${id}`);
  return response.json();
}

// Potential null pointer
function getUsername(user) {
  return user.profile.name.toUpperCase();
}

export { processUserData, memoizedFib, fetchUser, getUsername };
