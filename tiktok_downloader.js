const Tiktok = require('@tobyg74/tiktok-api-dl');

const url = process.argv[2];
if (!url) {
    console.log(JSON.stringify({status: 'error', message: 'URL required'}));
    process.exit(1);
}

(async () => {
    try {
        // Try v1 first
        let data = await Tiktok.Downloader(url, { version: 'v1' });
        
        if (data.status === 'error') {
            // Try v2 as fallback
            const v2Data = await Tiktok.Downloader(url, { version: 'v2' });
            if (v2Data.status === 'success' && v2Data.result) {
                // Normalize v2 to match v1 structure
                data = {
                    status: 'success',
                    result: {
                        ...v2Data.result,
                        video: {
                            ...v2Data.result.video,
                            downloadAddr: v2Data.result.video?.playAddr || v2Data.result.video?.downloadAddr,
                        }
                    }
                };
            } else {
                console.log(JSON.stringify({status: 'error', message: v2Data.message || 'Both API versions failed'}));
                process.exit(1);
            }
        }
        
        if (data.status === 'success' && data.result) {
            const result = data.result;
            // Prefer playAddr (CDN URL) over downloadAddr (API endpoint) for direct MP4
            const videoUrl = result.video?.playAddr?.[0] || result.video?.downloadAddr?.[0];
            
            if (videoUrl) {
                console.log(JSON.stringify({
                    status: 'success',
                    video_url: videoUrl,
                    title: result.desc || 'TikTok Video',
                    author: result.author?.nickname || result.author?.uniqueId || 'Unknown'
                }));
            } else {
                console.log(JSON.stringify({status: 'error', message: 'Video URL not found in response'}));
                process.exit(1);
            }
        } else {
            console.log(JSON.stringify({status: 'error', message: data.message || 'Failed to download'}));
            process.exit(1);
        }
    } catch (error) {
        console.log(JSON.stringify({status: 'error', message: error.message}));
        process.exit(1);
    }
})();
