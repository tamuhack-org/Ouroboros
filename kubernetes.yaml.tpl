apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: ouroboros
  labels:
    app: ouroboros
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: ouroboros
    spec:
      containers:
      - name: ouroboros-app
        # Replace this with your project ID
        image: gcr.io/GOOGLE_CLOUD_PROJECT/ouroboros:COMMIT_SHA
        imagePullPolicy: Always
        env:
          - name: DATABASE_USER
            valueFrom:
              secretKeyRef:
                name: cloudsql
                key: username
          - name: DATABASE_PASSWORD
            valueFrom:
              secretKeyRef:
                name: cloudsql
                key: password
          - name: SECRET_KEY
            valueFrom:
              secretKeyRef:
                name: django-sk
                key: secret_key
          - name: SENDGRID_API_KEY
            valueFrom:
              secretKeyRef:
                name: sendgrid
                key: apikey
          - name: GOOGLE_APPLICATION_CREDENTIALS
            value: "/etc/storage-creds/django-storages-creds.json"
        volumeMounts:
          - name: django-storage-credentials
            mountPath: /etc/storage-creds
            readOnly: true
        ports:
        - containerPort: 8080
      - image: gcr.io/cloudsql-docker/gce-proxy:1.05
        name: cloudsql-proxy
        command: ["/cloud_sql_proxy", "--dir=/cloudsql",
                  "-instances=GOOGLE_CLOUD_PROJECT:us-central1:ouroboros=tcp:5432",
                  "-credential_file=/secrets/cloudsql/credentials.json"]
        volumeMounts:
          - name: cloudsql-oauth-credentials
            mountPath: /secrets/cloudsql
            readOnly: true
          - name: ssl-certs
            mountPath: /etc/ssl/certs
          - name: cloudsql
            mountPath: /cloudsql
      volumes:
        - name: cloudsql-oauth-credentials
          secret:
            secretName: cloudsql-oauth-credentials
        - name: ssl-certs
          hostPath:
            path: /etc/ssl/certs
        - name: cloudsql
          emptyDir:
        - name: django-storage-credentials
          secret:
            secretName: django-storages-creds

---

apiVersion: v1
kind: Service
metadata:
  name: ouroboros-nodeport-service
spec:
  type: NodePort
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  selector:
    app: ouroboros

---

apiVersion: networking.gke.io/v1beta1
kind: ManagedCertificate
metadata:
  name: ouroboros-certificate
spec:
  domains:
    - tamuhack.com

---

apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: ouroboros-ingress
  annotations:
    kubernetes.io/ingress.global-static-ip-name:  34.67.144.238
    networking.gke.io/managed-certificates: ouroboros-certificate
spec:
  backend:
    serviceName: ouroboros-nodeport-service
    servicePort: 80