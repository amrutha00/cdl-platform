import { useEffect } from 'react';
import useUserDataStore from "../store/userData";


const WebSocketManager = () => {
   
    const {user_id, isLoggedOut, socket, setUserDataStoreProps} = useUserDataStore();
    console.log("user_id",user_id,isLoggedOut,socket);

    useEffect(() => {
        
        if (!isLoggedOut && user_id && !socket) {
            const websocketUrl = 'ws://localhost:8090/'; 
            const newSocket = new WebSocket(websocketUrl);

            newSocket.onopen = function(event) {
                console.log('WebSocket connection established');
                let message = JSON.stringify({
                    type: 'register',
                    user_id: user_id
                });
                setUserDataStoreProps({socket:newSocket});
                newSocket.send(message);
                console.log('Registration message sent:', message);
            };

            newSocket.onmessage = function(event) {
                console.log('Message from server:', event.data);
            };

            newSocket.onclose = function(event) {
                console.log('WebSocket connection closed');
                console.log('Code:', event.code);
                console.log('Reason:', event.reason);
                setUserDataStoreProps({socket:newSocket});
            };

            newSocket.onerror = function(error) {
                console.log('WebSocket error:', error);
            };
           
        }
    }, [isLoggedOut, user_id, socket]);


    return null;
};

export default WebSocketManager;
