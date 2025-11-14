from typing import Self, cast

import faiss  # type: ignore
import numpy as np
from scipy.linalg.blas import sgemm  # type: ignore


class KMeans:
    """K-means clustering using FAISS.

    Attributes:
        n_clusters (int): The number of clusters to form.
        n_iter (int): The number of iterations to run the k-means
            algorithm.
        n_local_trials  (int | None): The number of seeding trials for
            centroids initialization.
        random_state (int | None) Determines random number generation for
            centroid initialization.
        cluster_centers_ (np.ndarray | None): Coordinates of cluster centers.
        labels_ (np.ndarray | None): Labels of each point (index) in X.
    """

    n_clusters: int
    n_iter: int
    n_local_trials: int | None
    random_state: int | None
    cluster_centers_: np.ndarray | None
    labels_: np.ndarray | None

    def __init__(
        self,
        n_clusters: int,
        n_iter: int,
        n_local_trials: int | None,
        random_state: int | None,
    ):
        """Initializes the KMeans class.

        Args:
            n_clusters (int): The number of clusters to form.
            n_iter (int): The number of iterations to run the k-means
                algorithm.
            n_local_trials (int | None): The number of seeding trials for
                centroids initialization.
            random_state (int | None) Determines random number generation for
                centroid initialization.
        """
        self.n_clusters = n_clusters
        self.n_iter = n_iter
        self.n_local_trials = n_local_trials
        self.random_state = random_state
        self.cluster_centers_ = None
        self.labels_ = None

    @staticmethod
    def _dists(X: np.ndarray, y: np.ndarray, XX: np.ndarray) -> np.ndarray:
        """Computes the pairwise distances between a fixed data matrix and some points.

        Args:
            X (np.ndarray): The fixed data matrix.
            y (np.ndarray): The non fixed points.
            XX (np.ndarray): The fixed matrix squared norm.

        Returns:
            np.ndarray: The computed pairwise distances.
        """
        yy = np.einsum("ij,ij->i", y, y)
        dists = XX - cast(np.ndarray, sgemm(2.0, X, y, trans_b=True)) + yy
        np.clip(dists, 0, None, out=dists)

        return dists

    def _init_centroids(self, X: np.ndarray) -> np.ndarray:
        """Initializes the centroids in a K-means++ fashion.

        Args:
            X (np.ndarray): The fixed data matrix.

        Returns:
            np.ndarray: The initialized centroids.
        """
        rng = np.random.default_rng(self.random_state)

        centroids = np.empty((self.n_clusters, X.shape[1]), dtype=X.dtype)
        centroids[0] = X[rng.integers(X.shape[0])]

        XX = np.einsum("ij,ij->i", X, X)[:, None]

        dists = self._dists(X, centroids[:1], XX).ravel()
        inertia = dists.sum()

        if self.n_local_trials is None:
            self.n_local_trials = 2 + int(np.log(self.n_clusters))

        for i in range(1, self.n_clusters):
            candidate_ids = rng.choice(
                X.shape[0], size=self.n_local_trials, p=dists / inertia
            )
            candidates = np.asfortranarray(X[candidate_ids])

            current_candidates_dists = self._dists(X, candidates, XX)
            candidates_dists = np.minimum(current_candidates_dists, dists[:, None])

            inertias = candidates_dists.sum(axis=0)
            best_inertia = inertias.argmin()
            best_candidate = candidate_ids[best_inertia]
            dists = candidates_dists[:, best_inertia]
            inertia = inertias[best_inertia]

            centroids[i] = X[best_candidate]

        return centroids

    @staticmethod
    def _validate_X(X: np.ndarray) -> np.ndarray:
        """Validates and converts the data matrix.

        Args:
            X (NDArray[np.float32  |  np.float64]): The fixed data matrix.

        Raises:
            ValueError: If `X``contains inf values.
            ValueError: If `X``contains NaN values.

        Returns:
            np.ndarray: The validated and converted data matrix.
        """
        X_f32 = X.astype(np.float32, order="F")

        if np.isinf(X_f32).any():
            raise ValueError("X must not contain inf values")
        if np.isnan(X_f32).any():
            raise ValueError("X must not contain NaN values")

        return X_f32

    def fit(self, X: np.ndarray) -> Self:
        """Run k-means clustering on the input data X.

        Args:
            X (np.ndarray): Input data matrix to cluster.

        Returns:
            Self: The fitted model.
        """
        X_f32 = self._validate_X(X)

        index = faiss.IndexFlatL2(X_f32.shape[1])
        kmeans = faiss.Clustering(X_f32.shape[1], self.n_clusters)

        init_centroids = self._init_centroids(X_f32)

        kmeans.centroids.resize(init_centroids.size)
        faiss.copy_array_to_vector(init_centroids.ravel(), kmeans.centroids)  # type: ignore
        kmeans.niter = self.n_iter
        kmeans.min_points_per_centroid = 0
        kmeans.max_points_per_centroid = -1
        kmeans.train(X_f32, index)  # type: ignore

        self.cluster_centers_ = cast(
            np.ndarray,
            faiss.vector_to_array(kmeans.centroids).reshape(  # type: ignore
                self.n_clusters, X_f32.shape[1]
            ),
        )
        self.labels_ = cast(np.ndarray, index.search(X_f32, 1)[1].ravel())  # type: ignore

        return self
