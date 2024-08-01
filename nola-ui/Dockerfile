# Dockerfile

# Use an official Node.js runtime as a parent image
FROM node:20

# Set the working directory in the container to /app
WORKDIR /nola-ui

# Add the current directory contents into the container at /app
ADD . /nola-ui

# Install any needed packages specified in package.json
RUN npm install

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run the command to start the Vue.js application
CMD ["npm", "run", "serve"]