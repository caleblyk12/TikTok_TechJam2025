import {useState} from 'react'


function ProductCard({product}){

    return(
        <>
            <div className="product-card">
                <h4>{product.name}</h4>
                <img src={product.url} alt={product.name}></img>
                <p>{product.price}</p>
            </div>
        </>
    )
}

export default ProductCard