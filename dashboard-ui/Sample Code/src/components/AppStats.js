import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://acit-3855-lab6-duppin.westus3.cloudapp.azure.com:8100/stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>User Registration</th>
							<th>Image upload</th>
						</tr>
						<tr>
							<td># UR: {stats['num_user_registration_events']}</td>
							<td># IU: {stats['num_image_upload_events']}</td>
						</tr>
						<tr>
							<td colspan="2">Max Age: {stats['max_age_reading']}</td>
						</tr>
						<tr>
							<td colspan="2">Number of same filetype('.jpg'): {stats['num_of_same_filetype_reading']}</td>
						</tr>
						<tr>
							<td colspan="2">Last Updated: {stats['last_update']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

            </div>
        )
    }
}
