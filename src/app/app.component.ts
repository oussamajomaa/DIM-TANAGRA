import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import * as L from 'leaflet'
// import "leaflet.markercluster"
import { Place } from './place';

@Component({
	selector: 'app-root',
	templateUrl: './app.component.html',
	styleUrls: ['./app.component.css']
})
export class AppComponent {
	title = 'mapping-emotion';
	text = ""
	map: any
	mainLayer: any
	loading = false

	places: Place[] = [
		{
			"latitude": 48.85341,
			"longitude": 2.3488,
			"name": "Paris",
			"country": "France",
			"negative_labels": "0",
			"neutral_labels": "0",
			"occurrences": 1,
			"overall_sentiment": "Positive",
			"positive_labels": "1",
		},
		{
			"latitude": 33.5130695,
			"longitude": 36.3095814,
			"name": "Damas",
			"country": "Syrie",
			"negative_labels": "0",
			"neutral_labels": "0",
			"occurrences": 2,
			"overall_sentiment": "Negative",
			"positive_labels": "1",
		},
		{
			"latitude": 41,
			"longitude": 12,
			"name": "Rome",
			"country": "Italie",
			"negative_labels": "0",
			"neutral_labels": "0",
			"occurrences": 4,
			"overall_sentiment": "Neutral",
			"positive_labels": "1",
		},
		{
			"latitude": 40.4167754,
			"longitude": -3.7037902,
			"name": "Madrid",
			"country": "Espagne",
			"negative_labels": "0",
			"neutral_labels": "0",
			"occurrences": 2,
			"overall_sentiment": "Negative",
			"positive_labels": "1",
		},
	{
			"latitude": 52.520007,
			"longitude": 13.404954,
			"name": "Berlin",
			"country": "Allemagne",
			"negative_labels": "0",
			"neutral_labels": "0",
			"occurrences": 3,
			"overall_sentiment": "Negative",
			"positive_labels": "1",
		},
		{
			"latitude": 43.300000,
			"longitude": 5.400000,
			"name": "Marseilles",
			"country": "France",
			"negative_labels": "0",
			"neutral_labels": "0",
			"occurrences": 3,
			"overall_sentiment": "Negative",
			"positive_labels": "1",
		},
		{
			"latitude": 41.015137,
			"longitude": 28.979530,
			"name": "Istanbul",
			"country": "Turkey",
			"negative_labels": "0",
			"neutral_labels": "0",
			"occurrences": 2,
			"overall_sentiment": "Positive",
			"positive_labels": "1",
		},
	]

	displayedItems: any = [];
	intermidiate: string[] = [];
	currentIndex: number = 0;
	constructor(private http: HttpClient) { }
	// places: any = []
	// getCoords() {
	// 	this.places = []
	// 	if (this.text) {
	// 		if (this.markers.length > 0) {
	// 			this.map.remove()
	// 			this.createMap()
	// 		}
	// 		this.places = []
	// 		this.loading = true
	// 		this.http.post('http://localhost:3333/text', JSON.stringify(this.text))
	// 			.subscribe((res: any) => {
	// 				this.places = res
	// 				console.log(this.places);
	// 				if (this.places.length > 0) {
	// 					this.createMarker(this.places)
	// 					this.displayItemWithDelay();
	// 					this.fitOnMap()
	// 				}
	// 				this.loading = false
	// 			})
	// 	}
	// }

	getCoords(){
		this.createMarker(this.places)
		this.displayItemWithDelay();
		this.fitOnMap()
	}
	

	displayItemWithDelay() {

		if (this.currentIndex < this.places.length) {
			this.createMarker(this.places)
			setTimeout(() => {
				this.map.addLayer(this.markers[this.currentIndex])
				this.displayedItems.push(this.places[this.currentIndex]);
				this.intermidiate = this.displayedItems
				this.currentIndex++;
				this.displayItemWithDelay();
				console.log(this.currentIndex);
				console.log(this.places.length);
			}, 1000); // 1000 milliseconds = 1 second

		}
	}




	ngAfterViewInit(): void {
		this.createMap()

	}


	createMap(lat = 0, lng = 0, z = 2) {
		this.map = L.map('map').setView([lat, lng], z);
			
		// L.control.zoom({ position: 'topright' })
		this.mainLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
			minZoom: 1,
			maxZoom: 20,
			attribution: 'OSM'
		});
		this.mainLayer.addTo(this.map);


	}

	chageRangeValue(e: any) {
		let newMarkers = this.markers.slice(0, e.target.value)
		
		this.map.remove()
		this.createMap()

		newMarkers.map(marker => this.map.addLayer(marker))
		this.fitOnMap()
		this.places.map((place: any) => this.intermidiate.push(place.name))
		this.displayedItems = this.intermidiate
		console.log(e.target.value);
		this.displayedItems = this.displayedItems.slice(0, e.target.value)
		console.log(this.displayedItems);

	}

	// cluster = new L.MarkerClusterGroup()
	markers: any[] = []
	marker: any
	smarkersLayer: any
	createMarker(places: Place[]) {
		// this.cluster = new L.MarkerClusterGroup()
		this.markers = []
		places.map(place => {
			let icon = new L.Icon({
				iconUrl: `assets/${place.overall_sentiment}.png`,
				iconSize: [24 * Math.sqrt(place.occurrences), 24 * Math.sqrt(place.occurrences)],
			})
			let marker = L.marker([place.latitude, place.longitude], { icon: icon })

			marker.bindPopup(`
				Name: ${place.name}<br>
				Lat: ${place.latitude}<br>
				Lng: ${place.longitude}<br>
				Emotion: ${place.overall_sentiment}<br>
				Occurence: ${place.occurrences}
				`)

			marker.on('mouseover', () => marker.openPopup())
			marker.on('mouseout', () => marker.closePopup())
			this.markers.push(marker)
			// this.cluster.addLayer(marker)
			// setTimeout(() => {
			// 	this.map.addLayer(marker)
			// }, place.time);
		})
	}



	bounds: any
	fitOnMap() {

		if (this.markers.length > 1) {
			if (this.markers[0]._latlng.lat != this.markers[this.markers.length - 1]._latlng.lat &&
				this.markers[0]._latlng.lng != this.markers[this.markers.length - 1]._latlng.lng) {
				this.bounds = L.featureGroup(this.markers);
				this.map.fitBounds(this.bounds.getBounds(), { padding: [0, 0] });
			}
		}
		if (this.markers.length === 1) {
			console.log(this.markers);
			let markers = []
			this.map.setView([this.markers[0]._latlng.lat, this.markers[0]._latlng.lng], 8)
			let marker1 = L.marker([this.markers[0]._latlng.lat, this.markers[0]._latlng.lng - 1])
			let marker2 = L.marker([this.markers[0]._latlng.lat, this.markers[0]._latlng.lng + 1])
			markers.push(marker1)
			markers.push(marker2)
			this.bounds = L.featureGroup(markers);
			this.map.fitBounds(this.bounds.getBounds(), { padding: [0, 0] });
		}

	}

	reset() {
		this.text = ""
		this.map.remove()
		this.createMap()
		// this.markers = []
		this.displayedItems = []
		this.intermidiate = []
		this.currentIndex = 0
	}

	center() {
		console.log(this.markers);

		this.fitOnMap()
	}
}
