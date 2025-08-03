// JavaScript window size collection methods:

// 1. Window dimensions (viewport size)
console.log('Window width:', window.innerWidth);
console.log('Window height:', window.innerHeight);

// 2. Screen dimensions (physical screen size)
console.log('Screen width:', screen.width);
console.log('Screen height:', screen.height);

// 3. Available screen space (excluding browser UI)
console.log('Available width:', screen.availWidth);
console.log('Available height:', screen.availHeight);

// 4. Document dimensions (page content size)
console.log('Document width:', document.documentElement.clientWidth);
console.log('Document height:', document.documentElement.clientHeight);

// 5. Get all dimensions at once
function getWindowDimensions() {
    return {
        // Viewport (what user sees)
        viewport: {
            width: window.innerWidth,
            height: window.innerHeight
        },
        // Physical screen
        screen: {
            width: screen.width,
            height: screen.height,
            availableWidth: screen.availWidth,
            availableHeight: screen.availHeight
        },
        // Document content
        document: {
            width: document.documentElement.clientWidth,
            height: document.documentElement.clientHeight
        }
    };
}

// 6. Listen for window resize events
window.addEventListener('resize', function() {
    const dimensions = getWindowDimensions();
    console.log('Window resized:', dimensions);
});

// 7. Get dimensions on page load
window.addEventListener('load', function() {
    const dimensions = getWindowDimensions();
    console.log('Initial dimensions:', dimensions);
});

// 8. Real-time monitoring (for debugging)
function monitorWindowSize() {
    setInterval(() => {
        const dims = getWindowDimensions();
        console.log('Current size:', dims.viewport.width + 'x' + dims.viewport.height);
    }, 1000); // Log every second
}

// 9. Check if mobile/desktop based on size
function isMobile() {
    return window.innerWidth < 768;
}

function isTablet() {
    return window.innerWidth >= 768 && window.innerWidth < 1024;
}

function isDesktop() {
    return window.innerWidth >= 1024;
}

// 10. Get device pixel ratio (for high-DPI displays)
console.log('Device pixel ratio:', window.devicePixelRatio);

// Usage examples:
const dimensions = getWindowDimensions();
console.log('All dimensions:', dimensions);

if (isMobile()) {
    console.log('Mobile device detected');
} else if (isTablet()) {
    console.log('Tablet device detected');
} else {
    console.log('Desktop device detected');
}
