import React, { useState, useCallback } from 'react';
import Cropper from 'react-easy-crop';
import { IoCloseOutline, IoCheckmarkOutline, IoRefreshOutline } from 'react-icons/io5';

const createImage = (url) =>
    new Promise((resolve, reject) => {
        const image = new Image();
        image.addEventListener('load', () => resolve(image));
        image.addEventListener('error', (error) => reject(error));
        image.setAttribute('crossOrigin', 'anonymous');
        image.src = url;
    });

async function getCroppedImg(imageSrc, pixelCrop, rotation = 0) {
    const image = await createImage(imageSrc);
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    const maxSize = Math.max(image.width, image.height);
    const safeArea = 2 * ((maxSize / 2) * Math.sqrt(2));

    canvas.width = safeArea;
    canvas.height = safeArea;

    ctx.translate(safeArea / 2, safeArea / 2);
    ctx.rotate((rotation * Math.PI) / 180);
    ctx.translate(-safeArea / 2, -safeArea / 2);

    ctx.drawImage(
        image,
        safeArea / 2 - image.width * 0.5,
        safeArea / 2 - image.height * 0.5
    );

    const data = ctx.getImageData(0, 0, safeArea, safeArea);

    canvas.width = pixelCrop.width;
    canvas.height = pixelCrop.height;

    ctx.putImageData(
        data,
        Math.round(0 - safeArea / 2 + image.width * 0.5 - pixelCrop.x),
        Math.round(0 - safeArea / 2 + image.height * 0.5 - pixelCrop.y)
    );

    return new Promise((resolve) => {
        canvas.toBlob((blob) => {
            resolve(blob);
        }, 'image/jpeg', 0.95);
    });
}

export default function ImageCropper({ image, onCropComplete, onCancel }) {
    const [crop, setCrop] = useState({ x: 0, y: 0 });
    const [zoom, setZoom] = useState(1);
    const [rotation, setRotation] = useState(0);
    const [croppedAreaPixels, setCroppedAreaPixels] = useState(null);

    const onCropChange = (crop) => {
        setCrop(crop);
    };

    const onZoomChange = (zoom) => {
        setZoom(zoom);
    };

    const onRotationChange = (rotation) => {
        setRotation(rotation);
    };

    const onCropCompleteCallback = useCallback((croppedArea, croppedAreaPixels) => {
        setCroppedAreaPixels(croppedAreaPixels);
    }, []);

    const handleSave = useCallback(async () => {
        try {
            const croppedImage = await getCroppedImg(image, croppedAreaPixels, rotation);
            onCropComplete(croppedImage);
        } catch (e) {
            console.error(e);
        }
    }, [image, croppedAreaPixels, rotation, onCropComplete]);

    const resetCrop = () => {
        setCrop({ x: 0, y: 0 });
        setZoom(1);
        setRotation(0);
    };

    return (
        <div className="cropper-modal">
            <div className="cropper-content">
                <div className="cropper-header">
                    <h3>Adjust Your Image</h3>
                    <button onClick={onCancel} className="cropper-close-btn">
                        <IoCloseOutline />
                    </button>
                </div>

                <div className="cropper-container">
                    <Cropper
                        image={image}
                        crop={crop}
                        zoom={zoom}
                        rotation={rotation}
                        aspect={16 / 9}
                        onCropChange={onCropChange}
                        onZoomChange={onZoomChange}
                        onRotationChange={onRotationChange}
                        onCropComplete={onCropCompleteCallback}
                    />
                </div>

                <div className="cropper-controls">
                    <div className="control-group">
                        <label>Zoom</label>
                        <input
                            type="range"
                            min={1}
                            max={5}
                            step={0.1}
                            value={zoom}
                            onChange={(e) => setZoom(parseFloat(e.target.value))}
                            className="slider"
                        />
                    </div>

                    <div className="control-group">
                        <label>Rotation</label>
                        <input
                            type="range"
                            min={0}
                            max={360}
                            step={1}
                            value={rotation}
                            onChange={(e) => setRotation(parseInt(e.target.value))}
                            className="slider"
                        />
                    </div>
                </div>

                <div className="cropper-actions">
                    <button onClick={resetCrop} className="btn-cropper-reset">
                        <IoRefreshOutline />
                        <span>Reset</span>
                    </button>
                    <div style={{ display: 'flex', gap: '0.75rem' }}>
                        <button onClick={onCancel} className="btn-cropper-cancel">
                            Cancel
                        </button>
                        <button onClick={handleSave} className="btn-cropper-save">
                            <IoCheckmarkOutline />
                            <span>Apply</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
