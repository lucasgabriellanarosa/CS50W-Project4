const like_logic = async(postId) =>{
    
    await fetch(`/like_post/${postId}`)
    .then(response => response.json())
    .then(result => {
        document.querySelector(`#number_likes_${result.post_id}`).innerHTML = `${result.post_likes_count}`

        liked_post_btn = document.querySelector(`#liked_post_btn_${result.post_id}`)

        if(result.liked){
            liked_post_btn.className = "fa-solid fa-thumbs-up"
        }else{
            liked_post_btn.className = "fa-regular fa-thumbs-up"
        }

    })

}


const update_following = async(profileUserId) =>{
    await fetch(`/get_following_count/${profileUserId}`)
    .then(response => response.json())
    .then(result => {
        follwing_count = document.querySelector("#follwing_count").innerHTML = `Following: ${result.following_count}`
        followers_count = document.querySelector("#followers_count").innerHTML = `Followers: ${result.followers_count}`
    })
}


const follow_logic = async(profileUserId) => {
    await fetch(`/follow_user/${profileUserId}`)
    .then(response => response.json())
    .then(result => {
        document.querySelector("#followContainer").innerHTML = `<button class="btn btn-outline-danger" onclick="unfollow_logic(${profileUserId})">Unfollow</button>`
        update_following(profileUserId)
    })
}


const unfollow_logic = async(profileUserId) => {
    await fetch(`/unfollow_user/${profileUserId}`)
    .then(response => response.json())
    .then(result => {
        document.querySelector("#followContainer").innerHTML = `<button class="btn btn-outline-primary" onclick="follow_logic(${profileUserId})">Follow</button>`
        update_following(profileUserId)
    })
}


const edit_post = async(postId) => {
    text = document.querySelector(`#postText_${postId}`).innerText

    document.querySelector(`#postText_${postId}`).innerHTML = `<textarea name='textArea_${postId}' id='textArea_${postId}'>${text}</textarea>`
    document.querySelector(`#editBtnContainer_${postId}`).innerHTML = `<button class="btn btn-success" onclick="save_edit('${postId}')">Save</button>`
    
}


const save_edit = async(postId) => {
    const newText = document.querySelector(`#textArea_${postId}`).value
    await fetch(`/save_edit/${postId}`, {
        method: "POST",
        body: JSON.stringify({
            newText: newText,
        })
    })
    .then(response => response.json())
    .then(result => {
        document.querySelector(`#postText_${postId}`).innerHTML = result.newText
        document.querySelector(`#editBtnContainer_${postId}`).innerHTML = `<button class="btn btn-primary" onclick="edit_post('${postId}')">Edit</button>`
    })
}