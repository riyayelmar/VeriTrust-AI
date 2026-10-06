/* =========================================================
   GLOBAL VARIABLES
========================================================= */

let maps = {};
let markers = {};

let activeCameraType = null;
let cameraStream = null;

let capturedPhotos = {
    correspondence: [],
    permanent: []
};

let videoStream = null;
let mediaRecorder = null;
let videoChunks = [];

let currentVideoType = null;


/* =========================================================
   DEFAULT LOCATION
========================================================= */

const INDIA_LAT = 20.5937;
const INDIA_LNG = 78.9629;


/* =========================================================
   INITIALIZE MAPS
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    createMap("correspondence");
    createMap("permanent");

    setupSameAddress();

});


/* =========================================================
   CREATE MAP
========================================================= */

function createMap(type) {

    const mapId = type + "-map";

    maps[type] = L.map(mapId).setView(
        [INDIA_LAT, INDIA_LNG],
        5
    );


    /*
       Carto dark tiles are used instead of the
       blocked OSM tile endpoint.
    */

    L.tileLayer(
        "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        {
            attribution:
                '&copy; OpenStreetMap contributors &copy; CARTO',
            maxZoom: 20
        }
    ).addTo(maps[type]);


    maps[type].on(
        "click",
        function (event) {

            setLocation(
                type,
                event.latlng.lat,
                event.latlng.lng,
                null
            );

        }
    );

}


/* =========================================================
   CURRENT LOCATION
========================================================= */

function getCurrentLocation(type) {

    const message =
        document.getElementById(
            type + "-location-message"
        );


    message.innerText =
        "Getting your current location...";


    if (!navigator.geolocation) {

        message.innerText =
            "Geolocation is not supported by this browser.";

        return;
    }


    navigator.geolocation.getCurrentPosition(

        function (position) {

            const lat =
                position.coords.latitude;

            const lng =
                position.coords.longitude;

            const accuracy =
                position.coords.accuracy;


            setLocation(
                type,
                lat,
                lng,
                accuracy
            );

        },

        function (error) {

            message.innerText =
                "Unable to get current location. Please allow location access.";

        },

        {
            enableHighAccuracy: true,
            timeout: 15000,
            maximumAge: 0
        }

    );

}


/* =========================================================
   SET LOCATION
========================================================= */

async function setLocation(
    type,
    lat,
    lng,
    accuracy
) {

    document.getElementById(
        type + "-latitude"
    ).value = lat;


    document.getElementById(
        type + "-longitude"
    ).value = lng;


    document.getElementById(
        type + "-location_accuracy"
    ).value =
        accuracy || "";


    maps[type].setView(
        [lat, lng],
        17
    );


    if (markers[type]) {

        markers[type].setLatLng(
            [lat, lng]
        );

    } else {

        markers[type] =
            L.marker(
                [lat, lng]
            ).addTo(
                maps[type]
            );

    }


    const message =
        document.getElementById(
            type + "-location-message"
        );


    message.innerText =
        "Getting address information...";


    const address =
        await reverseGeocode(
            lat,
            lng
        );


    if (address) {

        fillAddress(
            type,
            address
        );


        message.innerText =
            "✓ Location detected successfully.";

    } else {

        message.innerText =
            "Location detected. Address details could not be loaded.";

    }

}


/* =========================================================
   REVERSE GEOCODING
========================================================= */

async function reverseGeocode(
    lat,
    lng
) {

    try {

        const response =
            await fetch(
                "https://nominatim.openstreetmap.org/reverse?format=json&lat="
                + lat
                + "&lon="
                + lng
                + "&zoom=18&addressdetails=1",
                {
                    headers: {
                        "Accept":
                            "application/json"
                    }
                }
            );


        const data =
            await response.json();


        return data;

    }

    catch (error) {

        console.error(
            "Reverse geocoding error:",
            error
        );

        return null;

    }

}


/* =========================================================
   SEARCH LOCATION
========================================================= */

async function searchLocation(type) {

    const input =
        document.getElementById(
            type + "-search"
        );


    const query =
        input.value.trim();


    if (!query) {

        alert(
            "Please enter a location to search."
        );

        return;
    }


    const message =
        document.getElementById(
            type + "-location-message"
        );


    message.innerText =
        "Searching location...";


    try {

        const response =
            await fetch(
                "https://nominatim.openstreetmap.org/search?format=json&q="
                + encodeURIComponent(query)
                + "&limit=1&addressdetails=1",
                {
                    headers: {
                        "Accept":
                            "application/json"
                    }
                }
            );


        const results =
            await response.json();


        if (!results.length) {

            message.innerText =
                "Address not found.";

            return;
        }


        const result =
            results[0];


        const lat =
            parseFloat(result.lat);

        const lng =
            parseFloat(result.lon);


        setLocation(
            type,
            lat,
            lng,
            null
        );

    }

    catch (error) {

        console.error(error);

        message.innerText =
            "Location search failed.";

    }

}


/* =========================================================
   FILL ADDRESS
========================================================= */

function fillAddress(
    type,
    data
) {

    const address =
        data.address || {};


    setValue(
        type + "-house_no",
        address.house_number || ""
    );


    setValue(
        type + "-street",
        address.road || address.street || ""
    );


    setValue(
        type + "-area",
        address.suburb ||
        address.neighbourhood ||
        address.village ||
        ""
    );


    setValue(
        type + "-city",
        address.city ||
        address.town ||
        address.village ||
        ""
    );


    setValue(
        type + "-district",
        address.state_district ||
        address.county ||
        ""
    );


    setValue(
        type + "-state",
        address.state || ""
    );


    setValue(
        type + "-pincode",
        address.postcode || ""
    );

}


function setValue(
    id,
    value
) {

    const element =
        document.getElementById(id);

    if (element) {

        element.value = value;

    }

}


/* =========================================================
   SAME ADDRESS
========================================================= */

function setupSameAddress() {

    const checkbox =
        document.getElementById(
            "same_address"
        );


    const permanent =
        document.getElementById(
            "permanent-section"
        );


    checkbox.addEventListener(
        "change",
        function () {

            if (this.checked) {

                permanent.style.display =
                    "none";


                copyCorrespondenceToPermanent();

            } else {

                permanent.style.display =
                    "block";

            }

        }
    );

}


function copyCorrespondenceToPermanent() {

    const fields = [
        "house_no",
        "street",
        "area",
        "city",
        "district",
        "state",
        "pincode",
        "latitude",
        "longitude",
        "location_accuracy"
    ];


    fields.forEach(
        function (field) {

            const source =
                document.getElementById(
                    "correspondence-" + field
                );


            const target =
                document.getElementById(
                    "permanent-" + field
                );


            if (source && target) {

                target.value =
                    source.value;

            }

        }
    );

}


/* =========================================================
   CAMERA
========================================================= */

async function openCamera(type) {

    activeCameraType = type;


    const modal =
        document.getElementById(
            "cameraModal"
        );


    const video =
        document.getElementById(
            "cameraVideo"
        );


    try {

        cameraStream =
            await navigator.mediaDevices.getUserMedia(
                {
                    video: {
                        facingMode: "environment"
                    },
                    audio: false
                }
            );


        video.srcObject =
            cameraStream;


        modal.style.display =
            "flex";


        updateCameraOverlay();


        updatePhotoCounter();

    }

    catch (error) {

        alert(
            "Camera access denied or unavailable."
        );

        console.error(error);

    }

}


/* =========================================================
   CAMERA OVERLAY
========================================================= */

function updateCameraOverlay() {

    if (!activeCameraType) {
        return;
    }


    const type =
        activeCameraType;


    const lat =
        document.getElementById(
            type + "-latitude"
        ).value;


    const lng =
        document.getElementById(
            type + "-longitude"
        ).value;


    const city =
        document.getElementById(
            type + "-city"
        ).value;


    const state =
        document.getElementById(
            type + "-state"
        ).value;


    const pincode =
        document.getElementById(
            type + "-pincode"
        ).value;


    const text =
        document.getElementById(
            "cameraLocationText"
        );


    text.innerHTML =
        "📍 "
        + (city || "Location")
        + ", "
        + (state || "")
        + " - "
        + (pincode || "")
        + "<br>"
        + "GPS: "
        + (lat || "--")
        + ", "
        + (lng || "--")
        + "<br>"
        + new Date().toLocaleString();

}


/* =========================================================
   CAPTURE PHOTO
========================================================= */

function capturePhoto() {

    if (!cameraStream) {
        return;
    }


    const video =
        document.getElementById(
            "cameraVideo"
        );


    const canvas =
        document.getElementById(
            "cameraCanvas"
        );


    canvas.width =
        video.videoWidth;

    canvas.height =
        video.videoHeight;


    const ctx =
        canvas.getContext(
            "2d"
        );


    /* CAMERA IMAGE */

    ctx.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
    );


    /* =====================================
       LOCATION STAMP
    ====================================== */

    const type =
        activeCameraType;


    const city =
        document.getElementById(
            type + "-city"
        ).value;


    const state =
        document.getElementById(
            type + "-state"
        ).value;


    const pincode =
        document.getElementById(
            type + "-pincode"
        ).value;


    const lat =
        document.getElementById(
            type + "-latitude"
        ).value;


    const lng =
        document.getElementById(
            type + "-longitude"
        ).value;


    const currentDate =
        new Date();


    const dateText =
        currentDate.toLocaleDateString();


    const timeText =
        currentDate.toLocaleTimeString();


    /* DARK STAMP */

    const stampHeight =
        Math.min(
            125,
            canvas.height * .20
        );


    ctx.fillStyle =
        "rgba(0,0,0,.68)";


    ctx.fillRect(
        0,
        canvas.height - stampHeight,
        canvas.width,
        stampHeight
    );


    ctx.fillStyle =
        "#ffffff";


    ctx.font =
        Math.max(
            16,
            canvas.width / 65
        )
        + "px Arial";


    let y =
        canvas.height -
        stampHeight +
        25;


    ctx.fillText(
        "VERITRUST AI",
        20,
        y
    );


    y += 24;


    ctx.font =
        Math.max(
            13,
            canvas.width / 82
        )
        + "px Arial";


    ctx.fillText(
        "📍 "
        + (city || "Location")
        + ", "
        + (state || "")
        + " - "
        + (pincode || ""),
        20,
        y
    );


    y += 22;


    ctx.fillText(
        "GPS: "
        + (lat || "--")
        + ", "
        + (lng || "--"),
        20,
        y
    );


    y += 22;


    ctx.fillText(
        dateText
        + "  "
        + timeText,
        20,
        y
    );


    /* =====================================
       CREATE IMAGE FILE
    ====================================== */

    canvas.toBlob(
        function (blob) {

            const file =
                new File(
                    [
                        blob
                    ],
                    "veritrust_home_"
                    + Date.now()
                    + ".jpg",
                    {
                        type:
                            "image/jpeg"
                    }
                );


            capturedPhotos[
                activeCameraType
            ].push(file);


            if (
                capturedPhotos[
                    activeCameraType
                ].length > 2
            ) {

                capturedPhotos[
                    activeCameraType
                ].shift();

            }


            updatePhotoInput(
                activeCameraType
            );


            updatePhotoPreview(
                activeCameraType
            );


            updatePhotoCounter();


            if (
                capturedPhotos[
                    activeCameraType
                ].length === 2
            ) {

                setTimeout(
                    closeCamera,
                    500
                );

            }

        },

        "image/jpeg",
        .92
    );

}


/* =========================================================
   UPDATE PHOTO INPUT
========================================================= */

function updatePhotoInput(type) {

    const input =
        document.getElementById(
            type + "-building_photos"
        );


    const dataTransfer =
        new DataTransfer();


    capturedPhotos[type].forEach(
        function (file) {

            dataTransfer.items.add(
                file
            );

        }
    );


    input.files =
        dataTransfer.files;

}


/* =========================================================
   PHOTO PREVIEW
========================================================= */

function updatePhotoPreview(type) {

    const container =
        document.getElementById(
            type + "-photo-preview"
        );


    container.innerHTML = "";


    capturedPhotos[type].forEach(
        function (file) {

            const image =
                document.createElement(
                    "img"
                );


            image.src =
                URL.createObjectURL(
                    file
                );


            container.appendChild(
                image
            );

        }
    );

}


/* =========================================================
   PHOTO COUNTER
========================================================= */

function updatePhotoCounter() {

    const counter =
        document.getElementById(
            "photoCounter"
        );


    if (!activeCameraType) {
        return;
    }


    counter.innerText =
        "Photo "
        + capturedPhotos[
            activeCameraType
        ].length
        + " / 2";

}


/* =========================================================
   CLOSE CAMERA
========================================================= */

function closeCamera() {

    const modal =
        document.getElementById(
            "cameraModal"
        );


    modal.style.display =
        "none";


    if (cameraStream) {

        cameraStream
            .getTracks()
            .forEach(
                track =>
                    track.stop()
            );

        cameraStream =
            null;

    }

}


/* =========================================================
   VIDEO CAMERA
========================================================= */

async function openVideoCamera(type) {

    currentVideoType =
        type;


    const modal =
        document.getElementById(
            "videoModal"
        );


    const video =
        document.getElementById(
            "recordVideo"
        );


    try {

        videoStream =
            await navigator.mediaDevices.getUserMedia(
                {
                    video: {
                        facingMode: "environment"
                    },
                    audio: true
                }
            );


        video.srcObject =
            videoStream;


        modal.style.display =
            "flex";


        updateVideoOverlay();

    }

    catch (error) {

        alert(
            "Camera and microphone permission is required."
        );

        console.error(error);

    }

}


/* =========================================================
   VIDEO OVERLAY TEXT
========================================================= */

function updateVideoOverlay() {

    const type =
        currentVideoType;


    const lat =
        document.getElementById(
            type + "-latitude"
        ).value;


    const lng =
        document.getElementById(
            type + "-longitude"
        ).value;


    const city =
        document.getElementById(
            type + "-city"
        ).value;


    const state =
        document.getElementById(
            type + "-state"
        ).value;


    const pincode =
        document.getElementById(
            type + "-pincode"
        ).value;


    document.getElementById(
        "videoLocationText"
    ).innerHTML =

        "📍 "
        + (city || "Location")
        + ", "
        + (state || "")
        + " - "
        + (pincode || "")
        + "<br>"
        + "GPS: "
        + (lat || "--")
        + ", "
        + (lng || "--")
        + "<br>"
        + new Date().toLocaleString();

}


/* =========================================================
   START VIDEO RECORDING
========================================================= */

function startVideoRecording() {

    if (!videoStream) {
        return;
    }


    const video =
        document.getElementById(
            "recordVideo"
        );


    const canvas =
        document.getElementById(
            "recordCanvas"
        );


    canvas.width =
        video.videoWidth || 1280;


    canvas.height =
        video.videoHeight || 720;


    const ctx =
        canvas.getContext(
            "2d"
        );


    const canvasStream =
        canvas.captureStream(
            30
        );


    /* AUDIO */

    const audioTracks =
        videoStream.getAudioTracks();


    audioTracks.forEach(
        function (track) {

            canvasStream.addTrack(
                track
            );

        }
    );


    mediaRecorder =
        new MediaRecorder(
            canvasStream,
            {
                mimeType:
                    "video/webm"
            }
        );


    videoChunks = [];


    mediaRecorder.ondataavailable =
        function (event) {

            if (
                event.data.size > 0
            ) {

                videoChunks.push(
                    event.data
                );

            }

        };


    mediaRecorder.onstop =
        function () {

            const blob =
                new Blob(
                    videoChunks,
                    {
                        type:
                            "video/webm"
                    }
                );


            const file =
                new File(
                    [
                        blob
                    ],
                    "veritrust_address_video_"
                    + Date.now()
                    + ".webm",
                    {
                        type:
                            "video/webm"
                    }
                );


            const input =
                document.getElementById(
                    currentVideoType
                    + "-video"
                );


            const dataTransfer =
                new DataTransfer();


            dataTransfer.items.add(
                file
            );


            input.files =
                dataTransfer.files;


            showVideoPreview(
                currentVideoType,
                file
            );

        };


    mediaRecorder.start();


    drawRecordingFrame(
        ctx,
        canvas,
        video
    );


    document.getElementById(
        "startRecordingBtn"
    ).disabled = true;


    document.getElementById(
        "stopRecordingBtn"
    ).disabled = false;


    document.getElementById(
        "recordingStatus"
    ).innerText =
        "🔴 Recording...";


}


/* =========================================================
   DRAW VIDEO FRAME
========================================================= */

function drawRecordingFrame(
    ctx,
    canvas,
    video
) {

    if (
        !mediaRecorder ||
        mediaRecorder.state !== "recording"
    ) {

        return;

    }


    ctx.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
    );


    const type =
        currentVideoType;


    const city =
        document.getElementById(
            type + "-city"
        ).value;


    const state =
        document.getElementById(
            type + "-state"
        ).value;


    const pincode =
        document.getElementById(
            type + "-pincode"
        ).value;


    const lat =
        document.getElementById(
            type + "-latitude"
        ).value;


    const lng =
        document.getElementById(
            type + "-longitude"
        ).value;


    const stampHeight =
        Math.min(
            130,
            canvas.height * .20
        );


    ctx.fillStyle =
        "rgba(0,0,0,.68)";


    ctx.fillRect(
        0,
        canvas.height - stampHeight,
        canvas.width,
        stampHeight
    );


    ctx.fillStyle =
        "#ffffff";


    ctx.font =
        Math.max(
            16,
            canvas.width / 65
        )
        + "px Arial";


    let y =
        canvas.height -
        stampHeight +
        25;


    ctx.fillText(
        "VERITRUST AI",
        20,
        y
    );


    y += 24;


    ctx.font =
        Math.max(
            13,
            canvas.width / 82
        )
        + "px Arial";


    ctx.fillText(
        "📍 "
        + (city || "Location")
        + ", "
        + (state || "")
        + " - "
        + (pincode || ""),
        20,
        y
    );


    y += 22;


    ctx.fillText(
        "GPS: "
        + (lat || "--")
        + ", "
        + (lng || "--"),
        20,
        y
    );


    y += 22;


    ctx.fillText(
        new Date().toLocaleString(),
        20,
        y
    );


    requestAnimationFrame(
        function () {

            drawRecordingFrame(
                ctx,
                canvas,
                video
            );

        }
    );

}


/* =========================================================
   STOP VIDEO
========================================================= */

function stopVideoRecording() {

    if (
        mediaRecorder &&
        mediaRecorder.state === "recording"
    ) {

        mediaRecorder.stop();

    }


    if (videoStream) {

        videoStream
            .getTracks()
            .forEach(
                track =>
                    track.stop()
            );

        videoStream =
            null;

    }


    document.getElementById(
        "startRecordingBtn"
    ).disabled = false;


    document.getElementById(
        "stopRecordingBtn"
    ).disabled = true;


    document.getElementById(
        "recordingStatus"
    ).innerText =
        "Video saved.";


    setTimeout(
        function () {

            document.getElementById(
                "videoModal"
            ).style.display =
                "none";

        },
        700
    );

}


/* =========================================================
   VIDEO PREVIEW
========================================================= */

function showVideoPreview(
    type,
    file
) {

    const container =
        document.getElementById(
            type + "-video-preview"
        );


    container.innerHTML = "";


    const video =
        document.createElement(
            "video"
        );


    video.controls = true;


    video.src =
        URL.createObjectURL(
            file
        );


    container.appendChild(
        video
    );

}