export interface Place {
    id?: string,
    name: string,
    latitude: number,
    longitude: number,
    country:string,
    occurrences: number,
    negative_labels:string,
    neutral_labels:string,
    positive_labels:string,
    overall_sentiment:string,
}