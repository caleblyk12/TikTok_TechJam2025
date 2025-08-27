import {useState} from 'react'

const productImages = {
  1: "https://example.com/tiktok-hoodie.jpg",
  2: "https://example.com/tiktok-cap.jpg",
  5: "https://example.com/medium-water-bottle.jpg",
  6: "https://example.com/small-water-bottle.jpg",
  7: "https://example.com/large-water-bottle.jpg",
};

function ProductCard({product}){

    return(
        <>
            <div className="product-card">
                <h4>{product.name}</h4>
                <img src={productImages[product.id]} alt={product.name}></img>
                <p>{product.price}</p>
            </div>
        </>
    )
}

export default ProductCard